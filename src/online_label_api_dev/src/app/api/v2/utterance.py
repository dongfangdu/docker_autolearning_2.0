# -*- coding: utf-8 -*-
import logging

from datetime import datetime
from flask import current_app
from sqlalchemy import desc, asc, or_

from app.libs.builtin_extend import datetime2timestamp
from app.libs.enums import UtteranceStatusEnum
from app.libs.error_code import PageResultSuccess, ResultSuccess, ParameterException
from app.libs.qpaginate import pager
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db_v2, DB_V2_TABLE_PREFIX
from app.models.v2.engine.ng import NgDitingRelation, NgDiting
from app.models.v2.engine.utterance import UtteranceAudio, UtteranceAccess
from app.models.v2.web.label import LabelUtteranceInfo, LabelResult, LabelTask, LabelDitingInfo
from app.validators.base import PageForm, ColumnSortForm
from app.validators.forms_v2 import UtteranceSearchForm, LabelTaskIDForm, UtteranceRefSearchForm, UtteranceSVSearchForm, \
    UtteranceIDListForm

api = Redprint('uttr')
logger = logging.getLogger(__name__)


@api.route('/list-unref-proj', methods=['POST'])
@auth.login_required
def utterance_list_unref_project():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    form = UtteranceRefSearchForm().validate_for_api()

    q = db_v2.session.query(UtteranceAudio, UtteranceAccess).filter(
        UtteranceAudio.is_deleted == 0,
        UtteranceAccess.is_deleted == 0,
        UtteranceAudio.request_id == UtteranceAccess.request_id,
        or_(UtteranceAudio.uttr_status == UtteranceStatusEnum.PARSED.value,
            UtteranceAudio.uttr_status == UtteranceStatusEnum.SELECTED.value)
    )

    if form.stt_time_left.data:
        q = q.filter(UtteranceAccess.time >= datetime.fromtimestamp(form.stt_time_left.data))
    if form.stt_time_right.data:
        q = q.filter(UtteranceAccess.time <= datetime.fromtimestamp(form.stt_time_right.data))
    q = q.order_by(desc(UtteranceAccess.time), UtteranceAccess.id)

    offset_var = 0
    if form.ord_num_begin.data:
        offset_var = int(form.ord_num_begin.data) - 1
        if offset_var < 1:
            offset_var = 0
    q = q.offset(offset_var)
    if form.ord_num_end.data:
        limit_var = int(form.ord_num_end.data) - offset_var
        if limit_var > 1:
            q = q.limit(limit_var)
    q_final = db_v2.session.query(q.subquery('inner_q', with_labels=True))

    # print q_final
    rvs = pager(q_final, page=cur_page, per_page=per_page)

    vms = []
    for rv in rvs.items:
        rv_dict = {c: getattr(rv, c, None) for c in rv._fields}
        vm = {}
        vm['request_id'] = rv_dict['{}_{}'.format(UtteranceAccess.__tablename__, 'request_id')]
        vm['stt_time'] = datetime2timestamp(rv_dict['{}_{}'.format(UtteranceAccess.__tablename__, 'time')])
        vm['detect_duration'] = rv_dict['{}_{}'.format(UtteranceAccess.__tablename__, 'detect_duration')]
        vms.append(vm)

    return PageResultSuccess(msg=u'未关联项目的语句列表', data=vms, page=rvs.page_view())


@api.route('/list-unref-task', methods=['POST'])
@auth.login_required
def utterance_list_unref_task():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    task_id = LabelTaskIDForm().validate_for_api().task_id.data
    label_task = LabelTask.query.filter_by(id=task_id).first_or_404()

    form = UtteranceRefSearchForm().validate_for_api()

    q = db_v2.session.query(LabelUtteranceInfo).filter(LabelUtteranceInfo.request_id == LabelResult.request_id,
                                                       LabelResult.proj_id == label_task.proj_id,
                                                       LabelResult.task_id == -1)

    if form.stt_time_left.data:
        q = q.filter(LabelUtteranceInfo.time >= datetime.fromtimestamp(form.stt_time_left.data))
    if form.stt_time_right.data:
        q = q.filter(LabelUtteranceInfo.time <= datetime.fromtimestamp(form.stt_time_right.data))
    q = q.order_by(desc(LabelUtteranceInfo.time), LabelUtteranceInfo.id)

    offset_var = 0
    if form.ord_num_begin.data:
        offset_var = int(form.ord_num_begin.data) - 1
        if offset_var < 1:
            offset_var = 0
    q = q.offset(offset_var)
    if form.ord_num_end.data:
        limit_var = int(form.ord_num_end.data) - offset_var
        if limit_var > 1:
            q = q.limit(limit_var)
    q_final = db_v2.session.query(q.subquery('q'))

    rvs = pager(q_final, page=cur_page, per_page=per_page)

    vms = []
    for label_utterance_info in rvs.items:
        vm = {}
        vm['request_id'] = label_utterance_info.request_id
        vm['stt_time'] = datetime2timestamp(label_utterance_info.time)
        vm['detect_duration'] = label_utterance_info.detect_duration
        vms.append(vm)

    return PageResultSuccess(msg=u'未关联任务的语句列表', data=vms, page=rvs.page_view())


@api.route('/list', methods=['POST'])
@auth.login_required
def utterance_list():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    form = UtteranceSearchForm().validate_for_api()
    column_name, column_order = ColumnSortForm.fetch_column_param(ColumnSortForm().validate_for_api())

    db_in_search = '{}engine'.format(DB_V2_TABLE_PREFIX)
    if form.proj_code.data is not None and form.proj_code.data != '':
        db_in_search = '{}web'.format(DB_V2_TABLE_PREFIX)
    if form.task_code.data is not None and form.task_code.data != '':
        db_in_search = '{}web'.format(DB_V2_TABLE_PREFIX)
    if form.label_status.data is not None and form.label_status.data != '':
        db_in_search = '{}web'.format(DB_V2_TABLE_PREFIX)

    if db_in_search == '{}engine'.format(DB_V2_TABLE_PREFIX):
        q = db_v2.session.query(UtteranceAudio, UtteranceAccess).filter(
            UtteranceAudio.is_deleted == 0,
            UtteranceAccess.is_deleted == 0,
            UtteranceAudio.request_id == UtteranceAccess.request_id
        ).order_by(desc(UtteranceAccess.time))
        if form.stt_time_left.data:
            q = q.filter(UtteranceAccess.time >= datetime.fromtimestamp(form.stt_time_left.data))
        if form.stt_time_right.data:
            q = q.filter(UtteranceAccess.time <= datetime.fromtimestamp(form.stt_time_right.data))

        rvs = pager(q, page=cur_page, per_page=per_page)

        vm_keys_uttr_aduio = ['request_id', 'url', 'truncation_ratio', 'volume', 'snr', ]
        vm_keys_uttr_access = ['time', 'result', 'real_rtf']
        vms = []
        for rv in rvs.items:
            rv_dict = {c: getattr(rv, c, None) for c in rv._fields}
            vm = {}
            for v_key in vm_keys_uttr_aduio:
                vm[v_key] = getattr(rv_dict['UtteranceAudio'], v_key, None)
            for v_key in vm_keys_uttr_access:
                vm[v_key] = getattr(rv_dict['UtteranceAccess'], v_key, None)
            vm['stt_time'] = datetime2timestamp(vm['time'])
            vms.append(vm)

        request_ids = list(set([vm['request_id'] for vm in vms]))
        label_result_list = db_v2.session.query(LabelResult).filter(
            LabelResult.is_deleted == 0,
            LabelResult.request_id.in_(request_ids)).all()
        label_result_dict = {label_result.request_id: label_result for label_result in label_result_list}

        vm_keys_label_result = ['label_status', 'label_text', 'wer', 'task_id', 'task_name', 'task_code', 'proj_id',
                                'proj_name', 'proj_code', ]
        vm_keys_label_result_default = {
            'label_status': 0
        }
        for vm in vms:
            for v_key in vm_keys_label_result:
                if label_result_dict.get(vm['request_id']):
                    vm[v_key] = getattr(label_result_dict[vm['request_id']], v_key, None)
                else:
                    vm[v_key] = vm_keys_label_result_default.get(v_key, None)
                vm['stt_time'] = datetime2timestamp(vm['time'])
                vm['uttr_url'] = (current_app.config['UTTERANCE_FILE_SERVER'] + vm['url']) if vm['url'] else None

        return PageResultSuccess(msg=u'语句管理列表', data=vms, page=rvs.page_view())

    if db_in_search == '{}web'.format(DB_V2_TABLE_PREFIX):
        q = db_v2.session.query(LabelUtteranceInfo, LabelResult).filter(
            LabelUtteranceInfo.request_id == LabelResult.request_id,
            LabelResult.is_deleted == 0
        ).order_by(desc(LabelUtteranceInfo.time))

        if form.stt_time_left.data:
            q = q.filter(LabelUtteranceInfo.time >= datetime.fromtimestamp(form.stt_time_left.data))
        if form.stt_time_right.data:
            q = q.filter(LabelUtteranceInfo.time <= datetime.fromtimestamp(form.stt_time_right.data))
        if form.proj_code.data is not None and form.proj_code.data != '':
            q = q.filter(LabelResult.proj_code.like('%' + form.proj_code.data + "%"))
        if form.task_code.data is not None and form.task_code.data != '':
            q = q.filter(LabelResult.task_code.like('%' + form.task_code.data + "%"))
        if form.label_status.data is not None and form.label_status.data != '':
            q = q.filter(LabelResult.label_status == form.label_status.data)

        rvs = pager(q, page=cur_page, per_page=per_page)
        vm_keys_uttr_info = ['request_id', 'url', 'truncation_ratio', 'volume', 'snr', 'time', 'result', 'real_rtf', ]
        vm_keys_label_result = ['label_status', 'label_text', 'wer', 'task_id', 'task_name', 'task_code', 'proj_id',
                                'proj_name', 'proj_code', ]
        vms = []
        for rv in rvs.items:
            rv_dict = {c: getattr(rv, c, None) for c in rv._fields}
            vm = {}
            for v_key in vm_keys_uttr_info:
                vm[v_key] = getattr(rv_dict['LabelUtteranceInfo'], v_key, None)
            for v_key in vm_keys_label_result:
                vm[v_key] = getattr(rv_dict['LabelResult'], v_key, None)
            vm['stt_time'] = datetime2timestamp(vm['time'])
            vm['uttr_url'] = (current_app.config['UTTERANCE_FILE_SERVER'] + vm['url']) if vm['url'] else None

            vms.append(vm)

        return PageResultSuccess(msg=u'语句管理列表', data=vms, page=rvs.page_view())

    return PageResultSuccess(msg=u'语句管理列表', data={}, page={'page': 1, 'limit': per_page, 'total': 0})


@api.route('/list-sv', methods=['POST'])
@auth.login_required
def utterance_list_supervisor():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())
    column_name, column_order = ColumnSortForm.fetch_column_param(ColumnSortForm().validate_for_api())

    form = UtteranceSVSearchForm().validate_for_api()

    column_obj_map = {
        '{}engine'.format(DB_V2_TABLE_PREFIX): {
            'id': UtteranceAudio.id,  # default

            'request_id': UtteranceAudio.request_id,
            'truncation_ratio': UtteranceAudio.truncation_ratio,
            'volume': UtteranceAudio.volume,
            'pre_snr': UtteranceAudio.pre_snr,
            'post_snr': UtteranceAudio.post_snr,

            'time': UtteranceAccess.time,
            'result': UtteranceAccess.result,
            'real_rtf': UtteranceAccess.real_rtf,
            'total_rtf': UtteranceAccess.total_rtf,
            'latency': UtteranceAccess.latency,
            'total_cost_time': UtteranceAccess.total_cost_time,
            'process_time': UtteranceAccess.process_time,
            'receive_cost_time': UtteranceAccess.receive_cost_time,
            'wait_cost_time': UtteranceAccess.wait_cost_time,
            'raw_rtf': UtteranceAccess.raw_rtf,
            'avg_packet_duration': UtteranceAccess.avg_packet_duration,
            'packet_count': UtteranceAccess.packet_count,
            'audio_format': UtteranceAccess.audio_format,
            'sample_rate': UtteranceAccess.sample_rate,
            'detect_duration': UtteranceAccess.detect_duration,

            'court_id': NgDitingRelation.court_id,
            'case_id': NgDitingRelation.case_id,
            'role_id': NgDitingRelation.role_id,

        },
        '{}web'.format(DB_V2_TABLE_PREFIX): {
            # 'id': LabelUtteranceInfo.id,  # default
            'label_text': LabelResult.label_text,
            'label_status': LabelResult.label_status,
            'wer': LabelResult.wer,
            'ins_cnt': LabelResult.ins_cnt,
            'sub_cnt': LabelResult.sub_cnt,
            'del_cnt': LabelResult.del_cnt,
        }
    }

    db_in_search = [db_name for db_name in column_obj_map.keys() if column_name in column_obj_map[db_name].keys()][0]
    if form.task_code.data and form.task_code.data != '':
        db_in_search = '{}web'.format(DB_V2_TABLE_PREFIX)
    if form.label_status.data is not None and form.label_status.data != '':
        db_in_search = '{}web'.format(DB_V2_TABLE_PREFIX)
    logger.info('searching db: {}'.format(db_in_search))

    if db_in_search == '{}engine'.format(DB_V2_TABLE_PREFIX):
        q = db_v2.session.query(UtteranceAudio, UtteranceAccess, NgDitingRelation).filter(
            UtteranceAudio.request_id == UtteranceAccess.request_id,
            UtteranceAccess.request_id == NgDiting.request_id,
            NgDiting.uuid == NgDitingRelation.uuid).filter(
            UtteranceAudio.is_deleted == 0,
            UtteranceAccess.is_deleted == 0
        )

        if form.label_time_left.data:
            q = q.filter(UtteranceAccess.time >= datetime.fromtimestamp(form.label_time_left.data))
        if form.label_time_right.data:
            q = q.filter(UtteranceAccess.time <= datetime.fromtimestamp(form.label_time_right.data))
        if form.court_id.data and form.court_id.data != '':
            q = q.filter(NgDitingRelation.court_id.like('%' + form.court_id.data + "%"))
        if form.case_id.data and form.case_id.data != '':
            q = q.filter(NgDitingRelation.case_id.like('%' + form.case_id.data + "%"))
        if form.role_id.data and form.role_id.data != '':
            q = q.filter(NgDitingRelation.role_id.like('%' + form.role_id.data + "%"))

        if column_order == 'ascending':
            q = q.order_by(asc(column_obj_map[db_in_search].get(column_name, UtteranceAudio.id)))
        else:
            q = q.order_by(desc(column_obj_map[db_in_search].get(column_name, UtteranceAudio.id)))

        rvs = pager(q, page=cur_page, per_page=per_page)

        vm_keys_uttr_audio = ['request_id', 'url', 'truncation_ratio', 'volume', 'pre_snr', 'post_snr', ]
        vm_keys_uttr_access = ['time', 'result', 'real_rtf', 'total_rtf', 'latency', 'total_cost_time', 'process_time',
                               'receive_cost_time', 'wait_cost_time', 'raw_rtf', 'avg_packet_duration', 'packet_count',
                               'audio_format', 'sample_rate', 'detect_duration', ]
        vm_keys_dt_rel = ['court_id', 'case_id', 'role_id', ]

        vms = []
        for rv in rvs.items:
            rv_dict = {c: getattr(rv, c, None) for c in rv._fields}
            vm = {}
            for v_key in vm_keys_uttr_audio:
                vm[v_key] = getattr(rv_dict['UtteranceAudio'], v_key, None)
            for v_key in vm_keys_uttr_access:
                vm[v_key] = getattr(rv_dict['UtteranceAccess'], v_key, None)
            for v_key in vm_keys_dt_rel:
                vm[v_key] = getattr(rv_dict['NgDitingRelation'], v_key, None)
            vm['stt_time'] = datetime2timestamp(vm['time'])
            vm['uttr_url'] = (current_app.config['UTTERANCE_FILE_SERVER'] + vm['url']) if vm['url'] else None

            vms.append(vm)

        #
        request_ids = list(set([vm['request_id'] for vm in vms]))
        label_result_list = db_v2.session.query(LabelResult).filter(
            LabelResult.is_deleted == 0,
            LabelResult.request_id.in_(request_ids)).all()
        label_result_dict = {label_result.request_id: label_result for label_result in label_result_list}
        #
        vm_keys_label_result = ['label_status', 'label_text', 'wer', 'ins_cnt', 'del_cnt', 'sub_cnt', 'task_id', ]
        vm_keys_label_result_default = {
            'label_status': 0
        }
        for vm in vms:
            for v_key in vm_keys_label_result:
                if label_result_dict.get(vm['request_id']):
                    # print label_result_dict[vm['request_id']]
                    vm[v_key] = getattr(label_result_dict[vm['request_id']], v_key, None)
                else:
                    vm[v_key] = vm_keys_label_result_default.get(v_key, None)

        task_ids = list(set([vm['task_id'] for vm in vms]))
        label_task_list = db_v2.session.query(LabelTask).filter(
            LabelTask.is_deleted == 0,
            LabelTask.id.in_(task_ids)).all()
        label_task_dict = {label_task.id: label_task for label_task in label_task_list}
        vm_keys_label_task = ['task_code', ]
        for vm in vms:
            for v_key in vm_keys_label_task:
                if label_task_dict.get(vm['task_id']):
                    vm[v_key] = getattr(label_task_dict[vm['task_id']], v_key, None)
                else:
                    vm[v_key] = None

        # for v_key in vm_keys_label_task:
        #     vm[v_key] = getattr(rvs_ex[vm['request_id']]['LabelTask'], v_key, None)

        return PageResultSuccess(msg=u'语句管理列表', data=vms, page=rvs.page_view())
    elif db_in_search == '{}web'.format(DB_V2_TABLE_PREFIX):
        q = db_v2.session.query(LabelUtteranceInfo, LabelDitingInfo, LabelResult).filter(
            LabelUtteranceInfo.request_id == LabelDitingInfo.request_id,
            LabelUtteranceInfo.request_id == LabelResult.request_id,
            LabelUtteranceInfo.is_deleted == 0,
            LabelDitingInfo.is_deleted == 0,
            LabelResult.is_deleted == 0,
        )

        if form.label_time_left.data:
            q = q.filter(LabelUtteranceInfo.time >= datetime.fromtimestamp(form.label_time_left.data))
        if form.label_time_right.data:
            q = q.filter(LabelUtteranceInfo.time <= datetime.fromtimestamp(form.label_time_right.data))
        if form.court_id.data and form.court_id.data != '':
            q = q.filter(LabelDitingInfo.court_id.like('%' + form.court_id.data + "%"))
        if form.case_id.data and form.case_id.data != '':
            q = q.filter(LabelDitingInfo.case_id.like('%' + form.case_id.data + "%"))
        if form.role_id.data and form.role_id.data != '':
            q = q.filter(LabelDitingInfo.role_id.like('%' + form.role_id.data + "%"))
        if form.task_code.data and form.task_code.data != '':
            q = q.filter(LabelResult.task_code.like('%' + form.task_code.data + "%"))
        if form.label_status.data is not None and form.label_status.data != '':
            q = q.filter(LabelResult.label_status == form.label_status.data)
        if column_order == 'ascending':
            q = q.order_by(asc(column_obj_map[db_in_search].get(column_name, LabelUtteranceInfo.id)))
        else:
            q = q.order_by(desc(column_obj_map[db_in_search].get(column_name, LabelUtteranceInfo.id)))

        rvs = pager(q, page=cur_page, per_page=per_page)

        vm_keys_uttr_info = ['request_id', 'url', 'truncation_ratio', 'volume', 'pre_snr', 'post_snr', 'time', 'result',
                             'real_rtf', 'total_rtf', 'latency', 'total_cost_time', 'process_time',
                             'receive_cost_time', 'wait_cost_time', 'raw_rtf', 'avg_packet_duration', 'packet_count',
                             'audio_format', 'sample_rate', 'detect_duration', ]
        vm_keys_dt_info = ['court_id', 'case_id', 'role_id', ]
        vm_keys_label_result = ['label_status', 'label_text', 'wer', 'ins_cnt', 'del_cnt', 'sub_cnt', 'task_id',
                                'task_code']
        vms = []
        for rv in rvs.items:
            rv_dict = {c: getattr(rv, c, None) for c in rv._fields}
            vm = {}
            for v_key in vm_keys_uttr_info:
                vm[v_key] = getattr(rv_dict['LabelUtteranceInfo'], v_key, None)
            for v_key in vm_keys_dt_info:
                vm[v_key] = getattr(rv_dict['LabelDitingInfo'], v_key, None)
            for v_key in vm_keys_label_result:
                vm[v_key] = getattr(rv_dict['LabelResult'], v_key, None)
            vm['stt_time'] = datetime2timestamp(vm['time'])
            vm['uttr_url'] = (current_app.config['UTTERANCE_FILE_SERVER'] + vm['url']) if vm['url'] else None

            vms.append(vm)
        return PageResultSuccess(msg=u'语句管理列表', data=vms, page=rvs.page_view())
    else:
        return PageResultSuccess(msg=u'语句管理列表', data={}, page={'page': cur_page, 'limit': per_page, 'total': 0})


@api.route('/calc-wer', methods=['POST'])
@auth.login_required
def utterance_calculate_wer():
    """
    计算被选语句中已标注语句的错误率. 若选中的语句均未标注,返回语句未标注的提示/异常.
    """
    req_id_list = UtteranceIDListForm().validate_for_api().req_id_list.data

    if not req_id_list or len(req_id_list) < 1:
        raise ParameterException(msg=u'未选中任何语句')

    rvs = []
    select_in_step = current_app.config['SQLALCHEMY_CUSTOM_SELECT_IN_STEP']  # TODO 封装
    select_in_from = 0
    select_in_to = select_in_from + select_in_step
    select_in_loop_counter = 0
    select_in_loop_counter_limit = int(len(req_id_list) / select_in_step) + 2
    while True:
        if len(req_id_list[select_in_from:select_in_to]) < 1 or select_in_loop_counter > select_in_loop_counter_limit:
            logger.debug('counter: {}'.format(select_in_loop_counter))
            break

        rvs_part = db_v2.session.query(LabelResult.ins_cnt, LabelResult.sub_cnt, LabelResult.del_cnt,
                                       LabelResult.label_text).filter(
            LabelResult.is_deleted == 0,
            LabelResult.label_status != 0,
            LabelResult.request_id.in_(req_id_list[select_in_from:select_in_to])).all()
        rvs += rvs_part

        select_in_from = select_in_to
        select_in_to = select_in_from + select_in_step
        select_in_loop_counter += 1
    logger.debug('length of {}: {}'.format('rvs', len(rvs)))

    # calc wer
    i, s, d, c = [0] * 4
    for rv in rvs:
        rv_dict = {c: getattr(rv, c, None) for c in rv._fields}
        i += rv_dict['ins_cnt'] or 0
        s += rv_dict['sub_cnt'] or 0
        d += rv_dict['del_cnt'] or 0
        c += len(rv_dict['label_text'] or '')
    wer = 100
    if c != 0:
        wer = float(i + s + d) / c * 100
    return ResultSuccess(msg=u'错误率计算成功', data={'wer': round(wer, 2)})


@api.route('/calc-all-wer', methods=['POST'])
@auth.login_required
def utterance_calculate_all_wer():
    form = UtteranceSearchForm().validate_for_api()

    q = db_v2.session.query(LabelResult.ins_cnt, LabelResult.sub_cnt, LabelResult.del_cnt,
                            LabelResult.label_text).filter(
        LabelUtteranceInfo.request_id == LabelResult.request_id,
        LabelResult.is_deleted == 0
    )

    if form.stt_time_left.data:
        q = q.filter(LabelUtteranceInfo.time >= datetime.fromtimestamp(form.stt_time_left.data))
    if form.stt_time_right.data:
        q = q.filter(LabelUtteranceInfo.time <= datetime.fromtimestamp(form.stt_time_right.data))
    if form.proj_code.data is not None and form.proj_code.data != '':
        q = q.filter(LabelResult.proj_code.like('%' + form.proj_code.data + "%"))
    if form.task_code.data is not None and form.task_code.data != '':
        q = q.filter(LabelResult.task_code.like('%' + form.task_code.data + "%"))
    if form.label_status.data is not None and form.label_status.data != '':
        q = q.filter(LabelResult.label_status == form.label_status.data)

    rvs = q.all()

    i, s, d, c = [0] * 4
    for rv in rvs:
        rv_dict = {c: getattr(rv, c, None) for c in rv._fields}
        i += rv_dict['ins_cnt'] or 0
        s += rv_dict['sub_cnt'] or 0
        d += rv_dict['del_cnt'] or 0
        c += len(rv_dict['label_text'] or '')
    wer = 100
    if c != 0:
        wer = float(i + s + d) / c * 100
    return ResultSuccess(msg=u'错误率计算成功', data={'wer': round(wer, 2)})


@api.route('/calc-all-sv-wer', methods=['POST'])
@auth.login_required
def utterance_calculate_all_sv_wer():  # TODO
    form = UtteranceSVSearchForm().validate_for_api()

    q = db_v2.session.query(LabelResult.ins_cnt, LabelResult.sub_cnt, LabelResult.del_cnt,
                            LabelResult.label_text).filter(
        LabelUtteranceInfo.request_id == LabelDitingInfo.request_id,
        LabelUtteranceInfo.request_id == LabelResult.request_id,
        LabelUtteranceInfo.is_deleted == 0,
        LabelDitingInfo.is_deleted == 0,
        LabelResult.is_deleted == 0,
        LabelResult.label_status != 0,
    )

    if form.label_time_left.data:
        q = q.filter(LabelUtteranceInfo.time >= datetime.fromtimestamp(form.label_time_left.data))
    if form.label_time_right.data:
        q = q.filter(LabelUtteranceInfo.time <= datetime.fromtimestamp(form.label_time_right.data))
    if form.court_id.data and form.court_id.data != '':
        q = q.filter(LabelDitingInfo.court_id.like('%' + form.court_id.data + "%"))
    if form.case_id.data and form.case_id.data != '':
        q = q.filter(LabelDitingInfo.case_id.like('%' + form.case_id.data + "%"))
    if form.role_id.data and form.role_id.data != '':
        q = q.filter(LabelDitingInfo.role_id.like('%' + form.role_id.data + "%"))
    if form.task_code.data and form.task_code.data != '':
        q = q.filter(LabelResult.task_code.like('%' + form.task_code.data + "%"))
    if form.label_status.data is not None and form.label_status.data != '':
        q = q.filter(LabelResult.label_status == form.label_status.data)

    rvs = q.all()

    i, s, d, c = [0] * 4
    for rv in rvs:
        rv_dict = {c: getattr(rv, c, None) for c in rv._fields}
        i += rv_dict['ins_cnt'] or 0
        s += rv_dict['sub_cnt'] or 0
        d += rv_dict['del_cnt'] or 0
        c += len(rv_dict['label_text'] or '')
    wer = 100
    if c != 0:
        wer = float(i + s + d) / c * 100
    return ResultSuccess(msg=u'错误率计算成功', data={'wer': round(wer, 2)})
