# -*- coding: utf8 -*-
import json
import logging
import os
import random
import time
import traceback
import codecs

import httplib2
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError

from src.app import create_app
from src.app.libs.builtin_extend import get_uuid, current_timestamp_sec
from src.app.models.base import db
from src.app.models.engine.prepare import PrepareRequestInfo, PrepareDataInfo
from src.app.models.engine.utterance import UtteranceAudio, UtteranceAccess
from src.app.models.label.labelraw import LabelrawResult, LabelrawUtteranceInfo
from src.app.models.test_target.prepare import PrepareTestData


def prepare_train_data(dp, p_uuid):
    time.sleep(1)
    prepare_status = 0
    prepare_data_path = None
    dp.logger.info(u'训练数据筛选处理开始')
    with dp.app.app_context():
        duration_limit = dp.app.config['DATA_SELECTION_TRAIN_DURATION_LIMIT']
        label_duration_limit = round(random.randint(5, 30) * duration_limit / 100)
        ng_duration_limit = duration_limit - label_duration_limit

        exclude_request_ids = set()
        exclude_rvs = db.session.query(PrepareDataInfo.request_id).filter(
            PrepareRequestInfo.prepare_uuid == PrepareDataInfo.prepare_uuid, PrepareRequestInfo.prepare_type == 2).all()
        exclude_request_ids = exclude_request_ids.union(set([request_id for request_id, in exclude_rvs]))

        # exclude_ng_set = set()

        prepare_data_info_list = []

        # 先准备标注数据
        rvs = db.session.query(LabelrawResult, LabelrawUtteranceInfo).outerjoin(LabelrawUtteranceInfo,
                                                                                LabelrawResult.request_id == LabelrawUtteranceInfo.request_id).all()

        total_cnt = len(rvs)

        loop_counter = 0
        loop_counter_limit = 50000

        duration_sum = 0
        duration_limit = label_duration_limit

        prepare_data_items = dict()
        while True:
            if loop_counter > loop_counter_limit:
                dp.logger.info(u'准备音频总时长 {} ms'.format(duration_sum))
                break
            if duration_sum > duration_limit:
                dp.logger.info(u'准备音频总时长 {} ms'.format(duration_sum))
                break

            idx = random.randint(0, total_cnt - 1)
            duration_sum += rvs[idx][1].detect_duration
            request_id = rvs[idx][0].request_id
            if request_id not in exclude_request_ids:
                prepare_data_items[request_id] = idx

            loop_counter += 1

        for i in prepare_data_items.values():
            data_info = PrepareDataInfo()
            data_info.prepare_uuid = p_uuid
            data_info.pdata_uuid = get_uuid()
            data_info.pdata_src_type = 1
            data_info.pdata_url = rvs[i][1].url
            data_info.pdata_text = rvs[i][0].label_text
            data_info.request_id = rvs[i][0].request_id
            data_info.uttr_url = rvs[i][1].url
            data_info.uttr_result = rvs[i][1].result
            data_info.uttr_duration = rvs[i][1].detect_duration
            data_info.label_uuid = rvs[i][0].label_uuid
            data_info.label_text = rvs[i][0].label_text
            prepare_data_info_list.append(data_info)

        # 识别数据
        exclude_request_ids = exclude_request_ids.union(prepare_data_items.keys())

        rvs = db.session.query(UtteranceAudio, UtteranceAccess).filter(
            UtteranceAudio.request_id == UtteranceAccess.request_id).order_by(desc(UtteranceAccess.time)).limit(
            50000).all()

        total_cnt = len(rvs)
        loop_counter = 0
        loop_counter_limit = 50000
        duration_sum = 0
        duration_limit = ng_duration_limit

        prepare_data_items = dict()
        while True:
            if loop_counter > loop_counter_limit:
                dp.logger.info(u'准备音频总时长 {} ms'.format(duration_sum))
                break
            if duration_sum > duration_limit:
                dp.logger.info(u'准备音频总时长 {} ms'.format(duration_sum))
                break

            idx = random.randint(0, total_cnt - 1)
            duration_sum += rvs[idx][1].detect_duration
            request_id = rvs[idx][0].request_id
            if request_id not in exclude_request_ids:
                prepare_data_items[request_id] = idx

            loop_counter += 1

        for i in prepare_data_items.values():
            data_info = PrepareDataInfo()
            data_info.prepare_uuid = p_uuid
            data_info.pdata_uuid = get_uuid()
            data_info.pdata_src_type = 2
            data_info.pdata_url = rvs[i][0].url
            data_info.pdata_text = rvs[i][1].result
            data_info.request_id = rvs[i][0].request_id
            data_info.uttr_url = rvs[i][0].url
            data_info.uttr_result = rvs[i][1].result
            data_info.uttr_duration = rvs[i][1].detect_duration
            data_info.label_uuid = None
            data_info.label_text = None
            prepare_data_info_list.append(data_info)
        # print len(prepare_data_info_list)

        try:
            with db.auto_commit():
                db.session.bulk_save_objects(prepare_data_info_list)
            dp.logger.info(u'训练数据入库成功')
            dp.logger.info(u'prepare_data_info入库条数：{}'.format(len(prepare_data_info_list)))
            prepare_status = 2

            #
            dp.logger.info(u'训练数据拉取开始')
            target_dir = dp.app.config['DATA_SELECTION_TRAIN_PREPARE_DIR']
            target_dir = os.path.join(target_dir, '{}/data'.format(p_uuid))
            target_dir = os.path.abspath(target_dir)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            for prepare_data_info in prepare_data_info_list:
                tmp_res = download_train_data(p_uuid, target_dir, prepare_data_info)
            dp.logger.info(u'训练数据拉取结束')
            prepare_data_path = target_dir
            prepare_status = 1

        except SQLAlchemyError:
            dp.logger.error(traceback.format_exc())
            dp.logger.info(u'测试数据入库失败')
            prepare_status = -1

    dp.logger.info(u'训练数据筛选处理开始')
    return {'dp': dp, 'prepare_uuid': p_uuid, 'prepare_status': prepare_status, 'prepare_data_path': prepare_data_path}


def download_train_data(p_uuid, target_dir, prepare_data_info):

    wav_target_dir = os.path.join(target_dir, 'wav')
    wav_target_dir = os.path.abspath(wav_target_dir)
    if not os.path.exists(wav_target_dir):
        os.mkdir(wav_target_dir)

    uttr_url = prepare_data_info.pdata_url
    filename = uttr_url.split('/')[-1]
    wav_target_filepath = os.path.join(wav_target_dir, filename)
    wav_target_filepath = os.path.abspath(wav_target_filepath)

    # print wav_target_filepath

    h = httplib2.Http()
    url = 'http://192.168.106.170:7779{}'.format(uttr_url)
    resp, content = h.request(url)
    if resp['status'] == '200':
        with open(wav_target_filepath, 'wb') as f:
            f.write(content)

    txt_target_dir = os.path.join(target_dir, 'txt')
    txt_target_dir = os.path.abspath(txt_target_dir)
    if not os.path.exists(txt_target_dir):
        os.mkdir(txt_target_dir)
    txt_target_filepath = os.path.join(txt_target_dir, 'wav_txt_map.txt')
    txt_target_filepath = os.path.abspath(txt_target_filepath)
    with codecs.open(txt_target_filepath, 'a+', encoding='utf-8') as f:
        f.write(u'{}\t{}\n'.format(filename, prepare_data_info.pdata_text))

    return True


def prepare_test_data(dp, p_uuid):
    time.sleep(1)
    dp.logger.info(u'测试数据筛选处理开始')
    prepare_status = 0
    prepare_data_path = None
    with dp.app.app_context():
        # 初始化过滤集
        exclude_request_ids = set()
        exclude_rvs = db.session.query(PrepareDataInfo.request_id).filter(
            PrepareRequestInfo.prepare_uuid == PrepareDataInfo.prepare_uuid, PrepareRequestInfo.prepare_type != 2).all()
        exclude_request_ids = exclude_request_ids.union(set([request_id for request_id, in exclude_rvs]))

        rvs = db.session.query(LabelrawResult, LabelrawUtteranceInfo).outerjoin(LabelrawUtteranceInfo,
                                                                                LabelrawResult.request_id == LabelrawUtteranceInfo.request_id).all()
        total_cnt = len(rvs)
        prepare_data_items = dict()
        loop_counter = 0
        loop_counter_limit = 50

        duration_sum = 0
        duration_limit = 7397000

        while True:
            if loop_counter > loop_counter_limit:
                dp.logger.info(u'准备音频总时长 {} ms'.format(duration_sum))
                break
            if duration_sum > duration_limit:
                dp.logger.info(u'准备音频总时长 {} ms'.format(duration_sum))
                break

            idx = random.randint(0, total_cnt - 1)
            duration_sum += rvs[idx][1].detect_duration
            request_id = rvs[idx][0].request_id
            if request_id not in exclude_request_ids:
                prepare_data_items[request_id] = idx

            loop_counter += 1

        test_target_list = []
        prepare_data_info_list = []
        for i in prepare_data_items.values():
            data_info = PrepareDataInfo()
            data_info.prepare_uuid = p_uuid
            data_info.pdata_uuid = get_uuid()
            data_info.pdata_src_type = 1
            data_info.pdata_url = rvs[i][1].url
            data_info.pdata_text = rvs[i][0].label_text
            data_info.request_id = rvs[i][0].request_id
            data_info.uttr_url = rvs[i][1].url
            data_info.uttr_result = rvs[i][1].result
            data_info.uttr_duration = rvs[i][1].detect_duration
            data_info.label_uuid = rvs[i][0].label_uuid
            data_info.label_text = rvs[i][0].label_text

            test_target = PrepareTestData()
            test_target.prepare_uuid = p_uuid
            test_target.request_id = rvs[i][0].request_id
            test_target.path = rvs[i][1].path
            test_target.url = rvs[i][1].url
            test_target.label_text = rvs[i][0].label_text

            prepare_data_info_list.append(data_info)
            test_target_list.append(test_target)

        try:
            with db.auto_commit():
                db.session.bulk_save_objects(prepare_data_info_list)
                db.session.bulk_save_objects(test_target_list)
            dp.logger.info(u'测试数据入库成功')
            dp.logger.info(u'prepare_data_info入库条数：{}'.format(len(prepare_data_info_list)))
            dp.logger.info(u'{}入库条数：{}'.format(PrepareTestData.__tablename__, len(test_target_list)))

            current_engine = db.get_engine(dp.app, PrepareTestData.__bind_key__)
            prepare_data_path = u'{}:{}/{}.{}'.format(current_engine.url.host, current_engine.url.port,
                                                      current_engine.url.database,
                                                      PrepareTestData.__tablename__)
            prepare_status = 1

        except SQLAlchemyError:
            dp.logger.error(traceback.format_exc())
            dp.logger.info(u'测试数据入库失败')
            prepare_status = -1

    dp.logger.info(u'测试数据筛选处理结束')
    return {'dp': dp, 'prepare_uuid': p_uuid, 'prepare_status': prepare_status, 'prepare_data_path': prepare_data_path}


def prepare_train_data_with_enhance(dp, p_uuid):
    time.sleep(1)
    dp.logger.info(u'训练（增强）数据筛选处理开始')
    with dp.app.app_context():
        pass

    dp.logger.info(u'训练（增强）数据筛选处理结束')
    return {'dp': dp, 'prepare_uuid': p_uuid, 'prepare_status': 1}


def finish_prepare_status(obj):
    res = obj.result()
    dp = res['dp']
    prepare_uuid = res['prepare_uuid']
    prepare_status = res['prepare_status']
    prepare_data_path = res['prepare_data_path']
    with dp.app.app_context():
        req_info = PrepareRequestInfo.query.filter(PrepareRequestInfo.prepare_uuid == prepare_uuid).first()
        try:
            with db.auto_commit():
                req_info.prepare_finish_time = current_timestamp_sec()
                req_info.prepare_status = prepare_status
                req_info.prepare_data_path = prepare_data_path
            dp.logger.info(u'数据准备请求修改：id: {}, prepare_uuid: {}, prepare_status: {}, prepare_data_path: {}'.format(
                req_info.id, req_info.prepare_uuid, req_info.prepare_status, req_info.prepare_data_path))
        except SQLAlchemyError:
            dp.logger.error(traceback.format_exc())
            dp.logger.info(u'数据准备请求修改失败')


class DataPrepare():
    def __init__(self, algorithm_name=None, config_filepath=None):
        self.excutor = ThreadPoolExecutor(max_workers=4)
        self.app = create_app(os.getenv('FLASK_CONFIG') or 'production')
        self.logger = logging.getLogger(__name__)
        self.algorithm_name = algorithm_name
        self.config_filepath = config_filepath

    def prepare_data(self, prepare_type):
        self.logger.info(u'**** {} ****'.format(u'数据准备接口调用开始'))
        self.logger.info(u'数据准备类型：{}'.format(prepare_type))

        prepare_uuid = None
        err_code = 2000
        try:
            prepare_uuid = self._inner_prepare_data(prepare_type=prepare_type)
        except Exception:
            self.logger.error(traceback.format_exc())
            err_code = 5000

        res = dict(prepare_uuid=prepare_uuid, err_code=err_code)
        res_json = json.dumps(res)
        self.logger.info(u'**** {} ****'.format(u'数据准备接口调用结束'))
        return res_json

    def _inner_prepare_data(self, prepare_type):
        p_uuid = get_uuid()
        self.logger.info(u'数据准备全局ID：{}'.format(p_uuid))
        with self.app.app_context():
            req_info = PrepareRequestInfo()

            req_info.prepare_uuid = p_uuid
            req_info.prepare_type = prepare_type
            req_info.prepare_start_time = current_timestamp_sec()
            req_info.prepare_status = 0
            req_info.prepare_finish_time = None

            try:
                with db.auto_commit():
                    db.session.add(req_info)
                self.logger.info(u'数据准备请求入库：id: {}, prepare_uuid: {}, prepare_status: {}'.format(
                    req_info.id, req_info.prepare_uuid, req_info.prepare_status))
            except SQLAlchemyError:
                self.logger.error(traceback.format_exc())
                self.logger.info(u'数据准备请求入库失败')
                p_uuid = None

            try:
                if prepare_type == 1:
                    self.logger.info(u'准备训练数据')
                    self.excutor.submit(prepare_train_data, self, p_uuid).add_done_callback(finish_prepare_status)
                elif prepare_type == 2:
                    self.logger.info(u'准备测试数据')
                    self.excutor.submit(prepare_test_data, self, p_uuid).add_done_callback(finish_prepare_status)
                elif prepare_type == 3:
                    self.logger.info(u'准备训练数据（含增强）')
                    self.excutor.submit(prepare_train_data_with_enhance(), self, p_uuid).add_done_callback(
                        finish_prepare_status)
                else:
                    self.logger.error(u'数据准备类型不存在')
                    p_uuid = None

            except Exception as e:
                raise e

        return p_uuid

    def is_ready(self, prepare_uuid):
        self.logger.info(u'数据准备状态询问：prepare_uuid: {}'.format(prepare_uuid))

        prepare_status = 0
        prepare_data_path = None
        err_code = 1000

        with self.app.app_context():
            req_info = PrepareRequestInfo.query.filter(PrepareRequestInfo.prepare_uuid == prepare_uuid).first()
            if not req_info:
                err_code = 4000
            else:
                prepare_status = req_info.prepare_status
                prepare_data_path = req_info.prepare_data_path
                err_code = 2000

        res = dict(prepare_uuid=prepare_uuid, prepare_status=prepare_status, prepare_data_path=prepare_data_path, err_code=err_code)
        res_json = json.dumps(res)

        return res_json

    def _do_async_internal_prepare(self):
        app = create_app(os.getenv('FLASK_CONFIG') or 'production')
        with app.app_context():
            resultproxy = db.session.execute('select 1;')
            results = resultproxy.fetchall()
            for result in results:
                print(result)


# if __name__ == '__main__':
#     dp = DataPrepare()
#     # print dp.prepare_data(prepare_type=1)
#     # p_res = json.loads(dp.prepare_data(prepare_type=1))
#     # prepare_uuid = p_res['prepare_uuid']
#     # print prepare_uuid
#     # # 86952a8263264d77bac8184c9a4f5c1c
#     # # f46a7cfacb134a79bc72e3dc09bdd94b
#     # # 09b3d0cac1694cd199d3ca291356c40c
#     # res = json.loads(dp.is_ready(prepare_uuid))
#     res = json.loads(dp.is_ready('25755439b37a49a9bcfba30be4ffc283'))
#
#     print 'prepare_status:', res['prepare_status']
#     print 'prepare_data_path:', res['prepare_data_path']
#     print 'err_code:', res['err_code']
#
#     # while True:
#     #     res = json.loads(dp.is_ready(prepare_id))
#     #     print 'prepare_status:', res['prepare_status']
#     #     print 'mock_data_path:', res['mock_data_path']
#     #     if res['prepare_status'] == 1:
#     #         break
#     #
#     #     time.sleep(4)
#
#     # import httplib2
#     # import os
#     #
#     # uttr_url = '/audios/2019/05/30/default/df086fecfca6482c0ac13f575390821e.wav'
#     # # uttr_url = '192.168.106.170:7779/audios/2019/05/31/default/f95a65cb889d201a8f667d57d74e9779.wav'
#     # target_dir = 'D:/train_tmp_data'
#     # filename = uttr_url.split('/')[-1]
#     # print filename
#     # target_filepath = os.path.join(target_dir, filename)
#     # target_filepath = os.path.abspath(target_filepath)
#     # print target_filepath
#     #
#     # h = httplib2.Http()
#     #
#     # url = 'http://192.168.106.170:7779{}'.format(uttr_url)
#     # resp, content = h.request(url)
#     #
#     # if resp['status'] == '200':
#     #     with open(target_filepath, 'wb') as f:
#     #         f.write(content)
#     #
#     # pass
