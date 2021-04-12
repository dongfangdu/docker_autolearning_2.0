# -*- coding: utf8 -*-
import json
import logging
import traceback

import os
import time
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.exc import SQLAlchemyError

from app import create_app
from app.libs.builtin_extend import get_uuid, current_timestamp_sec
from app.libs.enums import PrepareTypeEnum
from app.libs.prepare_method.label import prepare_web_data
from app.libs.prepare_method.test import prepare_test_data
from app.libs.prepare_method.train import prepare_train_data
from app.models.base import db_v2
from app.models.v2.engine.prepare import PrepareRequestInfo
import argparse

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
    prepare_type = res['prepare_type']
    prepare_data_path = res['prepare_data_path']
    prepare_data_cnt = res['prepare_data_cnt']
    train_loop_counter_limit = dp.app.config['TRAIN_LOOP_COUNTER_LIMIT']
    time_sleep = dp.app.config['TIME_SLEEP']
    with dp.app.app_context():
        req_info = PrepareRequestInfo.query.filter(PrepareRequestInfo.prepare_uuid == prepare_uuid).first()
        try:
            with db_v2.auto_commit():
                req_info.prepare_finish_time = current_timestamp_sec()
                req_info.prepare_status = prepare_status
                req_info.prepare_data_path = prepare_data_path
                if prepare_type == 1 and prepare_data_cnt < train_loop_counter_limit:
                    req_info.is_deleted = 1
                    dp.logger.info(u'数据准备请求修改：id: {}, prepare_uuid: {}, prepare_status: {}, prepare_data_path: {}, '
                                   u'is_deleted: {}'.format(req_info.id, req_info.prepare_uuid, req_info.prepare_status,
                                                            req_info.prepare_data_path, req_info.is_deleted))
                    dp.logger.info(u'训练数据准备量不足{}条,等待中...'.format(train_loop_counter_limit))
                    time.sleep(time_sleep)
                else:
                    req_info.is_deleted = 0
                    dp.logger.info(u'数据准备请求修改：id: {}, prepare_uuid: {}, prepare_status: {}, prepare_data_path: {}, '
                                   u'is_deleted: {}'.format(req_info.id, req_info.prepare_uuid, req_info.prepare_status,
                                                            req_info.prepare_data_path, req_info.is_deleted))
        except SQLAlchemyError:
            dp.logger.error(traceback.format_exc())
            dp.logger.info(u'数据准备请求修改失败')
        dp.logger.info(u'===================================================')


class DataPrepare():
    def __init__(self, algorithm_name=None, config_filepath=None):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.app = create_app(os.getenv('FLASK_CONFIG') or 'default', logging_cfg='./cfg/logging_ds.yaml')
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
                with db_v2.auto_commit():
                    db_v2.session.add(req_info)
                self.logger.info(u'数据准备请求入库：id: {}, prepare_uuid: {}, prepare_status: {}'.format(
                    req_info.id, req_info.prepare_uuid, req_info.prepare_status))
            except SQLAlchemyError:
                self.logger.error(traceback.format_exc())
                self.logger.info(u'数据准备请求入库失败')
                p_uuid = None

            try:
                if prepare_type == PrepareTypeEnum.TRAIN_DATA.value:
                    self.logger.info(u'准备训练数据')
                    self.executor.submit(prepare_train_data, self, p_uuid).add_done_callback(finish_prepare_status)
                elif prepare_type == PrepareTypeEnum.TEST_DATA.value:
                    self.logger.info(u'准备测试数据')
                    self.executor.submit(prepare_test_data, self, p_uuid).add_done_callback(finish_prepare_status)
                elif prepare_type == PrepareTypeEnum.ENHANCE_DATA.value:
                    self.logger.info(u'准备训练数据（含增强）')
                    self.executor.submit(prepare_train_data_with_enhance(), self, p_uuid).add_done_callback(
                        finish_prepare_status)
                elif prepare_type == PrepareTypeEnum.LABEL_DATA.value:
                    self.logger.info(u'准备预标注数据')
                    self.executor.submit(prepare_web_data, self, p_uuid).add_done_callback(finish_prepare_status)
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

        res = dict(prepare_uuid=prepare_uuid, prepare_status=prepare_status, prepare_data_path=prepare_data_path,
                   err_code=err_code)
        res_json = json.dumps(res)

        return res_json


if __name__ == '__main__':
    '''
    print '1231232132'
    dp = DataPrepare()
    # print dp.prepare_data(prepare_type=1)
    p_res = json.loads(dp.prepare_data(prepare_type=PrepareTypeEnum.TRAIN_DATA.value))
    prepare_uuid = p_res['prepare_uuid']
    print p_res
    print prepare_uuid
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--DATA_TYPE', action = 'store', required = True, help = 'input data type')
    inputargs = parser.parse_args()
    dp = DataPrepare()
    # print dp.prepare_data(prepare_type=1)
    p_res = json.loads(dp.prepare_data(prepare_type=int(inputargs.DATA_TYPE)))
    prepare_uuid = p_res['prepare_uuid']
    print p_res
    print prepare_uuid
#     # res = json.loads(dp.is_ready(prepare_uuid))
#     # # res = json.loads(dp.is_ready('142f0d7170554388b0d19229190b5498'))
# #
# #     print 'prepare_status:', res['prepare_status']
# #     print 'prepare_data_path:', res['prepare_data_path']
# #     print 'err_code:', res['err_code']
# #
# #     # while True:
# #     #     res = json.loads(dp.is_ready(prepare_id))
# #     #     print 'prepare_status:', res['prepare_status']
# #     #     print 'mock_data_path:', res['mock_data_path']
# #     #     if res['prepare_status'] == 1:
# #     #         break
# #     #
# #     #     time.sleep(4)
# #
