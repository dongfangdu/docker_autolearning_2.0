# -*- coding: utf8 -*-
import random
import traceback

from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError

from app.libs.builtin_extend import get_uuid
from app.libs.enums import UtteranceStatusEnum, PdataSrcTypeEnum, PrepareStatusEnum, PrepareTypeEnum
from app.models.base import db_v2
from app.models.v2.engine.prepare import PrepareDataInfo, PrepareRequestInfo
from app.models.v2.engine.utterance import UtteranceAudio, UtteranceAccess
from app.models.v2.web.label import LabelUtteranceInfo


def prepare_web_data(dp, p_uuid):
    prepare_status = PrepareStatusEnum.RUNNING.value
    prepare_data_path = None
    dp.logger.info(u'预标注数据筛选处理开始')
    with dp.app.app_context():
        # 此处在configure.py中增加了本次要挑选的总标注音频时长信息
        duration_limit = dp.app.config['DATA_SELECTION_WEB_LABEL_DURATION_LIMIT']

        exclude_request_ids = set()
        # 排除集，已挑选用于标注的数据的type为4，即prepare_type == 4
        exclude_rvs = db_v2.session.query(PrepareDataInfo.request_id).filter(
            PrepareRequestInfo.prepare_uuid == PrepareDataInfo.prepare_uuid,
            PrepareRequestInfo.prepare_type == PrepareTypeEnum.LABEL_DATA.value).all()
        exclude_rvs = exclude_rvs + db_v2.session.query(LabelUtteranceInfo.request_id).all()

        exclude_request_ids = exclude_request_ids.union(set([request_id for request_id, in exclude_rvs]))
        # 构建两个列表：用于后续数据库对应表的内容插入
        prepare_data_info_list = []
        label_utterance_info_list = []
        uttr_audio_update_list = []
        # 挑选预标注数据
        q = db_v2.session.query(UtteranceAudio, UtteranceAccess).filter(
            UtteranceAudio.request_id == UtteranceAccess.request_id
        ).order_by(desc(UtteranceAccess.time)).limit(2000)
        print q.count()
        rvs = q.all()
        print(rvs)
        print(rvs[0])
        print('+++++++++++++++')
        print(rvs[0][0])
        print(rvs[0][1].real_rtf)
        print(rvs[0][1].result)
        print('=====================')
        total_cnt = len(rvs)
        prepare_loop_counter = 0
        # 1个短音频按照1s来算，10小时的话数量为36000，设置prepare_loop_counter_limit = 50000
        prepare_loop_counter_limit = 50000

        duration_sum = 0

        prepare_data_items = dict()
        while True:
            if prepare_loop_counter > prepare_loop_counter_limit:
                dp.logger.info(u'准备音频总时长 {} ms'.format(duration_sum))
                break
            if duration_sum >= duration_limit:
                dp.logger.info(u'准备音频总时长 {} ms'.format(duration_sum))
                break

            idx = random.randint(0, total_cnt - 1)
            request_id = rvs[idx][0].request_id
            real_rtf = rvs[idx][1].real_rtf
            if request_id not in exclude_request_ids and request_id not in prepare_data_items.keys() and real_rtf < 0.4:
                prepare_data_items[request_id] = idx
                duration_sum += rvs[idx][1].detect_duration

            prepare_loop_counter += 1
        print(prepare_data_items) 
        # 准备数据库表prepare_data_info和label_utterance_info的写入内容
        for i in prepare_data_items.values():
            uttr_audio_update_list.append(rvs[i][0])

            data_info = PrepareDataInfo()
            data_info.prepare_uuid = p_uuid
            data_info.pdata_uuid = get_uuid()
            # 1:标注，2：识别，3：增强
            data_info.pdata_src_type = PdataSrcTypeEnum.LABELED_SRC.value
            # print(rvs[i][0])
            data_info.pdata_url = rvs[i][0].url
            data_info.pdata_text = rvs[i][1].result
            data_info.request_id = rvs[i][0].request_id
            data_info.uttr_url = rvs[i][0].url
            data_info.uttr_result = rvs[i][1].result
            data_info.uttr_duration = rvs[i][1].detect_duration
            prepare_data_info_list.append(data_info)

            web_target = LabelUtteranceInfo()
            web_target.ng_version = rvs[i][1].ng_version
            web_target.request_id = rvs[i][0].request_id
            web_target.time = rvs[i][1].time
            web_target.app = rvs[i][1].app
            web_target.group = rvs[i][1].group
            web_target.ip = rvs[i][1].ip
            web_target.app_key = rvs[i][1].app_key
            web_target.session_id = rvs[i][1].session_id
            web_target.device_uuid = rvs[i][1].device_uuid
            web_target.uid = rvs[i][1].uid
            web_target.start_timestamp = rvs[i][1].start_timestamp
            web_target.latency = rvs[i][1].latency
            web_target.status_code = rvs[i][1].status_code
            web_target.status_message = rvs[i][1].status_message
            web_target.backend_apps = rvs[i][1].backend_apps
            web_target.duration = rvs[i][1].duration
            web_target.audio_format = rvs[i][1].audio_format
            web_target.audio_url = rvs[i][1].audio_url
            web_target.sample_rate = rvs[i][1].sample_rate
            web_target.method = rvs[i][1].method
            web_target.packet_count = rvs[i][1].packet_count
            web_target.avg_packet_duration = rvs[i][1].avg_packet_duration
            web_target.total_rtf = rvs[i][1].total_rtf
            web_target.raw_rtf = rvs[i][1].raw_rtf
            web_target.real_rtf = rvs[i][1].real_rtf
            web_target.detect_duration = rvs[i][1].detect_duration
            web_target.total_cost_time = rvs[i][1].total_cost_time
            web_target.receive_cost_time = rvs[i][1].receive_cost_time
            web_target.wait_cost_time = rvs[i][1].wait_cost_time
            web_target.process_time = rvs[i][1].process_time
            web_target.processor_id = rvs[i][1].processor_id
            web_target.user_id = rvs[i][1].user_id
            web_target.vocabulary_id = rvs[i][1].vocabulary_id
            web_target.keyword_list_id = rvs[i][1].keyword_list_id
            web_target.customization_id = rvs[i][1].customization_id
            web_target.class_vocabulary_id = rvs[i][1].class_vocabulary_id
            web_target.result = rvs[i][1].result
            web_target.group_name = rvs[i][1].group
            web_target.path = rvs[i][0].path
            web_target.url = rvs[i][0].url
            web_target.truncation_ratio = rvs[i][0].truncation_ratio
            web_target.volume = rvs[i][0].volume
            web_target.snr = rvs[i][0].snr
            web_target.pre_snr = rvs[i][0].pre_snr
            web_target.post_snr = rvs[i][0].post_snr
            web_target.uttr_status = UtteranceStatusEnum.SELECTED.value
            web_target.prepare_uuid = p_uuid

            label_utterance_info_list.append(web_target)

        # # 更新排除集的内容
        # exclude_request_ids = exclude_request_ids.union(prepare_data_items.keys())

        try:
            with db_v2.auto_commit():
                for uttr_audio in uttr_audio_update_list:
                    uttr_audio.uttr_status = UtteranceStatusEnum.SELECTED.value
                db_v2.session.bulk_save_objects(prepare_data_info_list)
                db_v2.session.bulk_save_objects(label_utterance_info_list)
            dp.logger.info(u'预标注数据入库成功')
            dp.logger.info(u'prepare_data_info入库条数：{}'.format(len(prepare_data_info_list)))
            # 增加./src/models/web目录，定义LabelUtteranceInfo
            dp.logger.info(u'{}入库条数：{}'.format(LabelUtteranceInfo.__tablename__, len(label_utterance_info_list)))

            current_engine = db_v2.get_engine(dp.app, LabelUtteranceInfo.__bind_key__)
            prepare_data_path = u'{}:{}/{}.{}'.format(current_engine.url.host, current_engine.url.port,
                                                      current_engine.url.database,
                                                      LabelUtteranceInfo.__tablename__)
            prepare_status = PrepareStatusEnum.FINISHED.value

        except SQLAlchemyError:
            dp.logger.error(traceback.format_exc())
            dp.logger.error(u'预标注数据入库失败')
            prepare_status = PrepareStatusEnum.FAILED.value

    return {'dp': dp, 'prepare_uuid': p_uuid, 'prepare_status': prepare_status, 'prepare_data_path': prepare_data_path}
