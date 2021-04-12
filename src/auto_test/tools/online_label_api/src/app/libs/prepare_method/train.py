# -*- coding: utf8 -*-
import random
import traceback

import codecs
import httplib2
import os
import time
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError

from app.libs.builtin_extend import get_uuid
from app.libs.enums import PrepareTypeEnum, PdataSrcTypeEnum, PrepareStatusEnum
from app.models.base import db_v2
from app.models.v2.engine.prepare import PrepareDataInfo, PrepareRequestInfo
from app.models.v2.engine.utterance import UtteranceAudio, UtteranceAccess
from app.models.v2.label.labelraw import LabelrawResult, LabelrawUtteranceInfo


def prepare_train_data(dp, p_uuid):
    time.sleep(1)
    prepare_status = PrepareStatusEnum.RUNNING.value
    prepare_data_path = None
    dp.logger.info(u'训练数据筛选处理开始')
    with dp.app.app_context():
        duration_limit = dp.app.config['DATA_SELECTION_TRAIN_DURATION_LIMIT']
        label_duration_limit = round(random.randint(5, 30) * duration_limit / 100)
        ng_duration_limit = duration_limit - label_duration_limit

        exclude_request_ids = set()
        exclude_rvs = db_v2.session.query(PrepareDataInfo.request_id).filter(
            PrepareRequestInfo.prepare_uuid == PrepareDataInfo.prepare_uuid,
            PrepareRequestInfo.prepare_type == PrepareTypeEnum.TEST_DATA.value).all()
        exclude_request_ids = exclude_request_ids.union(set([request_id for request_id, in exclude_rvs]))

        # exclude_ng_set = set()

        prepare_data_info_list = []

        # 先准备标注数据
        rvs = db_v2.session.query(
            LabelrawResult, LabelrawUtteranceInfo
        ).outerjoin(
            LabelrawUtteranceInfo,
            LabelrawResult.request_id == LabelrawUtteranceInfo.request_id
        ).all()

        total_cnt = len(rvs)
        if total_cnt < 1:
            prepare_status = PrepareStatusEnum.IDK.value
            return {'dp': dp, 'prepare_uuid': p_uuid, 'prepare_status': prepare_status,
                    'prepare_data_path': prepare_data_path}

        prepare_loop_counter = 0
        prepare_loop_counter_limit = 50000

        duration_sum = 0
        duration_limit = label_duration_limit

        prepare_data_items = dict()
        while True:
            if prepare_loop_counter > prepare_loop_counter_limit:
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

            prepare_loop_counter += 1

        for i in prepare_data_items.values():
            data_info = PrepareDataInfo()
            data_info.prepare_uuid = p_uuid
            data_info.pdata_uuid = get_uuid()
            data_info.pdata_src_type = PdataSrcTypeEnum.LABELED_SRC.value
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

        rvs = db_v2.session.query(UtteranceAudio, UtteranceAccess).filter(
            UtteranceAudio.request_id == UtteranceAccess.request_id).order_by(desc(UtteranceAccess.time)).limit(
            50000).all()

        total_cnt = len(rvs)
        prepare_loop_counter = 0
        prepare_loop_counter_limit = 50000
        duration_sum = 0
        duration_limit = ng_duration_limit

        prepare_data_items = dict()
        while True:
            if prepare_loop_counter > prepare_loop_counter_limit:
                dp.logger.info(u'准备音频总时长 {} ms'.format(duration_sum))
                break
            if duration_sum > duration_limit:
                dp.logger.info(u'准备音频总时长 {} ms'.format(duration_sum))
                break

            idx = random.randint(0, total_cnt - 1)
            duration_sum += rvs[idx][1].detect_duration
            request_id = rvs[idx][0].request_id
            real_rtf = rvs[idx][1].real_rtf
            if request_id not in exclude_request_ids and real_rtf < 0.5:
                prepare_data_items[request_id] = idx

            prepare_loop_counter += 1

        for i in prepare_data_items.values():
            data_info = PrepareDataInfo()
            data_info.prepare_uuid = p_uuid
            data_info.pdata_uuid = get_uuid()
            data_info.pdata_src_type = PdataSrcTypeEnum.RECOGNIZED_SRC.value
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
            with db_v2.auto_commit():
                db_v2.session.bulk_save_objects(prepare_data_info_list)
            dp.logger.info(u'训练数据入库成功')
            dp.logger.info(u'prepare_data_info入库条数：{}'.format(len(prepare_data_info_list)))
            prepare_status = PrepareStatusEnum.DB_DONE.value

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
            prepare_status = PrepareStatusEnum.FINISHED.value

        except SQLAlchemyError:
            dp.logger.error(traceback.format_exc())
            dp.logger.info(u'测试数据入库失败')
            prepare_status = PrepareStatusEnum.FAILED.value

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
