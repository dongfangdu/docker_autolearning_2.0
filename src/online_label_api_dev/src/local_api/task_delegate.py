# -*- coding: utf8 -*-


import logging

import os
import time
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import desc

from app import create_app
from app.libs.builtin_extend import current_timestamp_sec, datetime2timestamp
from app.libs.enums import LabelTaskStatusEnum, PrepareTypeEnum, PrepareStatusEnum
from app.models.base import db_v2
from app.models.v2.engine import PrepareRequestInfo
from app.models.v2.web.label import LabelTask, LabelUtteranceInfo, LabelResult


class TaskDelegate():
    def __init__(self, algorithm_name=None, config_filepath=None):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.app = create_app(os.getenv('FLASK_CONFIG') or 'default')
        self.logger = logging.getLogger(__name__)
        self.algorithm_name = algorithm_name
        self.config_filepath = config_filepath

    def delegate_web_label(self, prepare_uuid):
        with self.app.app_context():
            # db_v2
            rvs = db_v2.session.query(PrepareRequestInfo.prepare_status).filter(
                PrepareRequestInfo.is_deleted == 0,
                PrepareRequestInfo.prepare_uuid == prepare_uuid,
                PrepareRequestInfo.prepare_type == PrepareTypeEnum.LABEL_DATA.value,
            ).first()
            if not rvs:
                self.logger.error(u'数据集不存在 prepare_uuid: {}'.format(prepare_uuid))
                return

            delegate_loop_counter = 0
            delegate_loop_counter_limit = 100

            prepare_status = rvs[0]

            while True:
                if delegate_loop_counter > delegate_loop_counter_limit:
                    self.logger.error(
                        u'已循环{}次，数据集准备状态为 prepare_status: {}'.format(delegate_loop_counter, prepare_status))
                    break

                if prepare_status == PrepareStatusEnum.FINISHED.value:
                    self.logger.info(u'数据集 {} 已准备好'.format(prepare_uuid))
                    self.do_delegate_web_label(prepare_uuid)
                    break

                wait_time = 5
                if delegate_loop_counter == 0:
                    prepare_request_info = PrepareRequestInfo.query.filter(
                        PrepareRequestInfo.is_deleted == 0,
                        # PrepareRequestInfo.prepare_uuid == prepare_uuid,
                        PrepareRequestInfo.prepare_type == PrepareTypeEnum.LABEL_DATA.value,
                        PrepareRequestInfo.prepare_finish_time is not None,
                        PrepareRequestInfo.prepare_status == PrepareStatusEnum.FINISHED.value
                    ).order_by(desc(PrepareRequestInfo.id)).first()
                    if prepare_request_info:
                        wait_time = (prepare_request_info.prepare_finish_time - prepare_request_info.prepare_start_time)
                        wait_time = wait_time * 0.1  # TODO 真实场景比例大点
                    else:
                        wait_time = 180  # 冷启动等三分钟
                    # print wait_time

                time.sleep(wait_time)

                db_v2.session.remove()  # 不能删这行，不然下次查询还是原来表的值
                prepare_status, = db_v2.session.query(PrepareRequestInfo.prepare_status).filter(
                    PrepareRequestInfo.is_deleted == 0,
                    PrepareRequestInfo.prepare_uuid == prepare_uuid,
                    PrepareRequestInfo.prepare_type == PrepareTypeEnum.LABEL_DATA.value,
                ).first()

                delegate_loop_counter += 1

    def do_delegate_web_label(self, prepare_uuid):
        with self.app.app_context():
            # 验证是否需要分配任务
            utterance_info_list = LabelUtteranceInfo.query.filter(
                LabelUtteranceInfo.prepare_uuid == prepare_uuid,
                LabelUtteranceInfo.uttr_status == 1
            ).all()

            if len(utterance_info_list) < 1:
                self.app.logger.info(u'该数据集 {} 没有可分配语句'.format(prepare_uuid))
                return

            # 新建任务
            task_code_prefix = '{}'.format(self.app.config['BUSI_LBTASK_AUTO_SELECT_CODE_PREFIX'])

            placeholder_num = self.app.config['BUSI_LBTASK_AUTO_SELECT_CODE_PLACEHOLDER_NUM']
            task_code_list = LabelTask.query.with_entities(LabelTask.task_code).filter(
                LabelTask.task_code.like(task_code_prefix + '%')).filter_by(
                with_deleted=True).all()
            task_cnt_by_code = max(
                [int(task_code[-min(placeholder_num, len(task_code) - len(task_code_prefix)):]) for task_code, in
                 task_code_list]) if len(
                task_code_list) > 0 else 0
            task_code = task_code_prefix + str(task_cnt_by_code + 1).zfill(placeholder_num)
            task_name = u'挑选标注任务{}'.format(str(task_cnt_by_code + 1))

            label_task = LabelTask()
            label_task.task_name = task_name
            label_task.task_code = task_code
            label_task.create_uid = -1
            label_task.create_time = current_timestamp_sec()
            label_task.task_status = LabelTaskStatusEnum.INACTIVED.value
            with db_v2.auto_commit():
                db_v2.session.add(label_task)

            # 关联标注数据
            label_result_list = []
            current_t = current_timestamp_sec()

            for utterance_info in utterance_info_list:
                label_result = LabelResult()
                label_result.request_id = utterance_info.request_id
                label_result.uttr_url = utterance_info.url
                label_result.uttr_result = utterance_info.result
                label_result.uttr_stt_time = datetime2timestamp(utterance_info.time)
                label_result.proj_id = -1
                label_result.task_id = label_task.id
                label_result.task_code = label_task.task_code
                label_result.task_name = label_task.task_name
                label_result.create_time = current_t
                label_result_list.append(label_result)
            with db_v2.auto_commit():
                db_v2.session.bulk_save_objects(label_result_list)
                for utterance_info in utterance_info_list:
                    utterance_info.is_assigned = 1
                    utterance_info.uttr_status = 4

            pass


if __name__ == '__main__':
    p_uuid = 'f3ab9d4605d54ac0893c5ebbd2d9d21c'
    # p_uuid = 'f3ab9d4605d54ac0893c5ebbd2d9d213'
    TaskDelegate().delegate_web_label(p_uuid)
    pass
