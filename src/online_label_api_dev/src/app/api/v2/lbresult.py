# -*- coding: utf-8 -*-
import logging

from flask import current_app, g
from sqlalchemy import func, asc, desc

from app.libs.builtin_extend import namedtuple_with_defaults, current_timestamp_sec, get_uuid
from app.libs.calculate_i_s_d_wer import i_s_d_wer
from app.libs.enums import LabelTaskStatusEnum, LabelResultStatusEnum, UtteranceStatusEnum
from app.libs.error_code import PageResultSuccess, ResultSuccess, ParameterException
from app.libs.qpaginate import pager
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db_v2
from app.models.v2.engine.utterance import UtteranceAudio, UtteranceAccess
from app.models.v2.label.labelraw import LabelrawResult
from app.models.v2.web.label import LabelResult, LabelTask, LabelUtteranceInfo
from app.validators.base import PageForm, ColumnSortForm
from app.validators.forms_v2 import LabelResultEditForm, LabelTaskIDForm, LabelResultSearchForm

api = Redprint('lbres')
logger = logging.getLogger(__name__)

LabelResultViewListItemFields = (
    'id', 'request_id', 'uttr_stt_time', 'uttr_url', 'uttr_result', 'proj_id', 'proj_code', 'proj_name', 'task_id',
    'task_code', 'task_name', 'label_status', 'label_text', 'label_time', 'label_uid', 'label_counter', 'ins_cnt',
    'sub_cnt', 'del_cnt', 'wer', 'label_tag_person', 'label_tag_accent', 'label_tag_gender')
LabelResultViewListItem = namedtuple_with_defaults('LabelResultViewListItem', LabelResultViewListItemFields,
                                                   default_values=(None,) * len(LabelResultViewListItemFields))


@api.route('/list', methods=['POST'])
@auth.login_required
def label_result_list():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    task_id = LabelTaskIDForm().validate_for_api().task_id.data
    form = LabelResultSearchForm().validate_for_api()

    column_name, column_order = ColumnSortForm.fetch_column_param(ColumnSortForm().validate_for_api())

    q = db_v2.session.query(LabelResult, LabelUtteranceInfo).filter(
        LabelResult.request_id == LabelUtteranceInfo.request_id, LabelResult.task_id == task_id).filter_by()

    if form.label_status.data:
        q = q.filter(LabelResult.label_status == form.label_status.data)

    column_obj_map = {
        'id': LabelResult.id,  # default
        'label_status': LabelResult.label_status,
        'wer': LabelResult.wer,
        'truncation_ratio': LabelUtteranceInfo.truncation_ratio,
        'volume': LabelUtteranceInfo.volume,
        'pre_snr': LabelUtteranceInfo.pre_snr,
        'post_snr': LabelUtteranceInfo.post_snr,
        'real_rtf': LabelUtteranceInfo.real_rtf,
    }
    if column_order == 'ascending':
        q = q.order_by(asc(column_obj_map.get(column_name, LabelResult.label_status)), LabelResult.id)
    else:
        q = q.order_by(desc(column_obj_map.get(column_name, LabelResult.label_status)), LabelResult.id)

    rvs = pager(q, page=cur_page, per_page=per_page)

    vms = []
    for rv in rvs.items:
        rv_dict = {c: getattr(rv, c, None) for c in rv._fields}
        label_result = rv_dict['LabelResult']
        uttr_info = rv_dict['LabelUtteranceInfo']
        vm = LabelResultViewListItem()._asdict()
        vm = dict(zip(vm.keys(), [dict(vm, **label_result)[x] for x in vm.keys()]))
        vm['uttr_url'] = current_app.config['UTTERANCE_FILE_SERVER'] + uttr_info.url
        vms.append(vm)
    return PageResultSuccess(msg=u'标注语句列表', data=vms, page=rvs.page_view())


@api.route('/mark', methods=['POST'])
@auth.login_required
def label_result_mark():
    form = LabelResultEditForm().validate_for_api()

    label_result = LabelResult.query.filter(
        LabelResult.is_deleted == 0,
        LabelResult.request_id == form.request_id.data,
        LabelResult.task_id == form.task_id.data
    ).first_or_404()
    rv = db_v2.session.query(UtteranceAudio, UtteranceAccess).filter(
        UtteranceAudio.request_id == UtteranceAccess.request_id,
        UtteranceAudio.request_id == form.request_id.data,
    ).first()
    uttr_info = LabelUtteranceInfo.query.filter(LabelUtteranceInfo.request_id == form.request_id.data).first()
    if not uttr_info and not rv:
        raise ParameterException(msg=u'该语句不存在 request_id: {}'.format(form.request_id.data))

    uttr_audio_list = []
    # 同步web
    if not uttr_info and rv:
        uttr_audio, uttr_access = rv
        uttr_audio_list.append(uttr_audio)
        uttr_info = LabelUtteranceInfo()
        for v_key in uttr_audio.keys():
            if v_key in ['id', 'insert_time', 'is_deleted', ]:
                continue
            setattr(uttr_info, v_key, getattr(uttr_audio, v_key, None))
        for v_key in uttr_access.keys():
            if v_key in ['id', 'insert_time', 'is_deleted', ]:
                continue
            setattr(uttr_info, v_key, getattr(uttr_access, v_key, None))
        uttr_info.uttr_status = UtteranceStatusEnum.SELECTED.value

        with db_v2.auto_commit():
            db_v2.session.add(uttr_info)

    old_label_text = label_result.label_text
    is_real_change = False
    with db_v2.auto_commit():
        uttr_info.uttr_status = UtteranceStatusEnum.LABELED.value
        for uttr_audio in uttr_audio_list:
            uttr_audio.uttr_status = UtteranceStatusEnum.LABELED.value

        form.populate_obj(label_result)
        i, s, d, wer = i_s_d_wer(form.label_text.data, label_result.uttr_result)
        label_result.ins_cnt = i
        label_result.sub_cnt = s
        label_result.del_cnt = d
        label_result.wer = wer
        label_result.label_status = LabelResultStatusEnum.MARKED.value
        if form.label_text.data != old_label_text:
            is_real_change = True
            label_result.label_time = current_timestamp_sec()
            label_result.label_uid = g.user.uid
            label_result.label_counter = label_result.label_counter + 1

            labelraw_result = LabelrawResult()
            labelraw_result.label_uuid = get_uuid()
            labelraw_result.label_text = label_result.label_text
            labelraw_result.label_time = label_result.label_time
            labelraw_result.request_id = label_result.request_id
            labelraw_result.uttr_url = label_result.uttr_url
            db_v2.session.add(labelraw_result)

            # TODO
            # 标签相关处理

    label_task = LabelTask.query.filter_by(id=label_result.task_id).first()
    if label_task:
        if label_task.task_status == LabelTaskStatusEnum.ONGONING.value:
            rv = db_v2.session.query(LabelResult.label_status, func.count('*').label('cnt')).filter(
                LabelResult.task_id == label_task.id, LabelResult.is_deleted == 0).group_by(LabelResult.label_status)
            tag_total = 0
            tag_cnt = 0
            for status, cnt in rv:
                tag_total += cnt
                if status == 1:
                    tag_cnt += cnt

            if tag_total > 0 and tag_total == tag_cnt:
                with db_v2.auto_commit():
                    label_task.task_status = LabelTaskStatusEnum.FINISHED.value
                    label_task.finish_time = current_timestamp_sec()
        if label_task.task_status == LabelTaskStatusEnum.AUDITED_FAILED.value and is_real_change:
            with db_v2.auto_commit():
                label_task.task_status = LabelTaskStatusEnum.MODIFY.value

    return_data = {'label_time': label_result.label_time, 'wer': label_result.wer,
                   'label_status': label_result.label_status}

    return ResultSuccess(msg=u'标注成功', data=return_data)
