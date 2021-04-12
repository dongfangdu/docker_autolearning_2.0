# -*- coding: utf8 -*-
import random
import traceback

import time
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.functions import func

from app.libs.builtin_extend import get_uuid
from app.libs.enums import PrepareTypeEnum, PdataSrcTypeEnum, PrepareStatusEnum
from app.models.base import db_v2
from app.models.v2.engine.prepare import PrepareDataInfo, PrepareRequestInfo
from app.models.v2.web.label import LabelResult, LabelUtteranceInfo
from app.models.v2.label.labelraw import LabelrawResult, LabelrawUtteranceInfo
from app.models.v2.test.test import TestAsrAudioInfo
from sqlalchemy import or_, and_, not_


def prepare_test_data(dp, p_uuid):
    time.sleep(1)
    dp.logger.info(u'测试数据筛选处理开始')
    prepare_status = PrepareStatusEnum.RUNNING.value
    prepare_data_path = None
    with dp.app.app_context():
        # 初始化过滤集
        exclude_request_ids = set()
        exclude_rvs = db_v2.session.query(PrepareDataInfo.request_id).filter(
            PrepareRequestInfo.prepare_uuid == PrepareDataInfo.prepare_uuid,
            or_(PrepareRequestInfo.prepare_type == PrepareTypeEnum.TEST_DATA.value,
                PrepareRequestInfo.prepare_type == PrepareTypeEnum.TRAIN_DATA.value),
            PrepareRequestInfo.is_deleted == 0
        ).all()
        exclude_request_ids = exclude_request_ids.union(set([request_id for request_id, in exclude_rvs]))

        rvs = db_v2.session.query(LabelResult, LabelUtteranceInfo).outerjoin(
            LabelUtteranceInfo, LabelResult.request_id == LabelUtteranceInfo.request_id).filter(
            func.char_length(LabelResult.label_text) > 7,
            not_(LabelResult.label_text.like("%~%")),
            not_(LabelResult.label_text.op('regexp')('[0-9]'))
            ).all()
        total_cnt = len(rvs)
        prepare_data_items = dict()
        prepare_loop_counter = 0
        prepare_loop_counter_limit = 3000

        duration_sum = 0
        duration_limit = 739700000

        if total_cnt < 1:
            # prepare_status = PrepareStatusEnum.IDK.value
            # return {'dp': dp, 'prepare_uuid': p_uuid, 'prepare_status': prepare_status,
            #        'prepare_data_path': prepare_data_path}
            dp.logger.info(u'没有标注数据了')

        while True:
            if total_cnt < 1:
                break
            if prepare_loop_counter > prepare_loop_counter_limit:
                dp.logger.info(u'准备音频总时长 {} ms'.format(duration_sum))
                break
            if duration_sum > duration_limit:
                dp.logger.info(u'准备音频总时长 {} ms'.format(duration_sum))
                break

            idx = random.randint(0, total_cnt - 1)
            duration_sum += rvs[idx][1].detect_duration
            request_id = rvs[idx][0].request_id
            prepare_loop_counter += 1
            if request_id not in exclude_request_ids:
                prepare_data_items[request_id] = idx


        test_target_list = []
        prepare_data_info_list = []
        for i in prepare_data_items.values():
            data_info = PrepareDataInfo()
            data_info.prepare_uuid = p_uuid
            data_info.pdata_uuid = get_uuid()
            data_info.pdata_src_type = PdataSrcTypeEnum.LABELED_SRC.value
            # data_info.pdata_url = rvs[i][1].url
            # data_info.pdata_text = rvs[i][0].label_text
            # data_info.request_id = rvs[i][0].request_id
            # data_info.uttr_url = rvs[i][1].url
            # data_info.uttr_result = rvs[i][1].result
            # data_info.uttr_duration = rvs[i][1].detect_duration
            # data_info.label_uuid = rvs[i][0].label_uuid
            # data_info.label_text = rvs[i][0].label_text
            data_info.pdata_url = rvs[i][1].url
            data_info.pdata_text = rvs[i][0].label_text
            data_info.request_id = rvs[i][0].request_id
            data_info.uttr_url = rvs[i][1].url
            data_info.uttr_result = rvs[i][1].result
            data_info.uttr_duration = rvs[i][1].detect_duration
            data_info.label_uuid = rvs[i][0].label_uid
            data_info.label_text = rvs[i][0].label_text
            # test_target = TestAsrAudioInfo()
            test_target = TestAsrAudioInfo()
            test_target.data_uuid = p_uuid
            test_target.request_id = rvs[i][0].request_id
            test_target.path = rvs[i][1].path
            test_target.url = rvs[i][1].url
            test_target.label_text = rvs[i][0].label_text

            prepare_data_info_list.append(data_info)
            test_target_list.append(test_target)

        try:
            with db_v2.auto_commit():
                db_v2.session.bulk_save_objects(prepare_data_info_list)
                db_v2.session.bulk_save_objects(test_target_list)
            dp.logger.info(u'测试数据入库成功')
            dp.logger.info(u'prepare_data_info入库条数：{}'.format(len(prepare_data_info_list)))
            dp.logger.info(u'{}入库条数：{}'.format(TestAsrAudioInfo.__tablename__, len(test_target_list)))

            current_engine = db_v2.get_engine(dp.app, TestAsrAudioInfo.__bind_key__)
            prepare_data_path = u'{}:{}/{}.{}'.format(current_engine.url.host, current_engine.url.port,
                                                      current_engine.url.database,
                                                      TestAsrAudioInfo.__tablename__)
            prepare_status = PrepareStatusEnum.FINISHED.value

        except SQLAlchemyError:
            dp.logger.error(traceback.format_exc())
            dp.logger.info(u'测试数据入库失败')
            prepare_status = PrepareStatusEnum.FAILED.value

    prepare_type = PrepareTypeEnum.TEST_DATA.value
    dp.logger.info(u'测试数据筛选处理结束')
    return {'dp': dp, 'prepare_uuid': p_uuid, 'prepare_type': prepare_type, 'prepare_status': prepare_status, 'prepare_data_path': prepare_data_path, 'prepare_data_cnt': len(prepare_data_info_list)}
