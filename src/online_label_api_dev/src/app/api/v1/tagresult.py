# -*- coding: utf-8 -*-
import time
from flask import current_app
from sqlalchemy import func

from app.libs.builtin_extend import namedtuple_with_defaults
from app.libs.calculate_i_s_d_wer import i_s_d_wer
from app.libs.enums import TagTaskStatusEnum
from app.libs.error_code import PageResultSuccess, ResultSuccess
from app.libs.qpaginate import pager
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db_v1
from app.models.v1.tagfile import Utterance, UtteranceAccess, UtteranceTrace
from app.models.v1.tagproj import TagResult, TagTask
from app.validators.base import PageForm
from app.validators.forms_v1 import TagResultEditForm, TagTaskIDForm, TagResultSearchForm, IDForm

api = Redprint('tagresult')


@api.route('/list-untagged', methods=['POST'])
@auth.login_required
def tagresult_list_untagged():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    task_id = TagTaskIDForm().validate_for_api().task_id.data
    q = db_v1.session.query(TagResult, Utterance, UtteranceAccess.result.label('lexical_no_symbol')).filter(
        TagResult.request_id == UtteranceAccess.request_id,
        TagResult.request_id == Utterance.request_id).filter_by(
        task_id=task_id, tag_status=0)
    q2 = db_v1.session.query(TagResult, Utterance, UtteranceTrace.result.label('lexical_no_symbol')).filter(
        TagResult.request_id == UtteranceTrace.request_id,
        TagResult.request_id == Utterance.request_id).filter_by(
        task_id=task_id, tag_status=0)
    rvs = pager(q.union_all(q2), page=cur_page, per_page=per_page)

    vms = []
    for tagresult, utterance, lexical_no_symbol in rvs.items:
        vm = {}
        vm['request_id'] = tagresult.request_id
        vm['uttr_url'] = current_app.config['UTTERANCE_FILE_SERVER'] + utterance.url
        vm['label_text'] = tagresult.label_text if tagresult.label_text else lexical_no_symbol
        vm['tag_status'] = tagresult.tag_status
        vms.append(vm)
    return PageResultSuccess(msg=u'未标注语句列表', data=vms, page=rvs.page_view())


@api.route('/list-tagged', methods=['POST'])
@auth.login_required
def tagresult_list_tagged():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    task_id = TagTaskIDForm().validate_for_api().task_id.data

    q = db_v1.session.query(TagResult, Utterance, UtteranceAccess.result.label('lexical_no_symbol')).filter(
        TagResult.request_id == UtteranceAccess.request_id,
        TagResult.request_id == Utterance.request_id).filter_by(
        task_id=task_id, tag_status=1)

    q2 = db_v1.session.query(TagResult, Utterance, UtteranceTrace.result.label('lexical_no_symbol')).filter(
        TagResult.request_id == UtteranceTrace.request_id,
        TagResult.request_id == Utterance.request_id).filter_by(
        task_id=task_id, tag_status=1)
    rvs = pager(q.union_all(q2), page=cur_page, per_page=per_page)

    vms = []
    for tagresult, utterance, lexical_no_symbol in rvs.items:
        vm = {}
        vm['request_id'] = tagresult.request_id
        vm['uttr_url'] = current_app.config['UTTERANCE_FILE_SERVER'] + utterance.url
        vm['label_text'] = tagresult.label_text if tagresult.label_text else lexical_no_symbol
        vm['tag_status'] = tagresult.tag_status
        vms.append(vm)
    return PageResultSuccess(msg=u'已标注语句列表', data=vms, page=rvs.page_view())


TagResultViewListItemFields = (
    'id', 'request_id', 'proj_id', 'task_id', 'tag_status', 'label_text', 'label_time', 'insertion_count', 'sub_count',
    'delete_count', 'wer', 'person', 'accent', 'gender', 'create_time')
TagResultViewListItem = namedtuple_with_defaults('TagResultViewListItem', TagResultViewListItemFields,
                                                 default_values=(None,) * len(TagResultViewListItemFields))


@api.route('/list', methods=['POST'])
@auth.login_required
def tagresult_list():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    task_id = TagTaskIDForm().validate_for_api().task_id.data
    form = TagResultSearchForm().validate_for_api()
    column_name = form.column_name.data
    column_order = form.column_order.data

    q = db_v1.session.query(
        TagResult.request_id.label('request_id'),
        TagResult.id.label('id'),
        TagResult.create_time.label('create_time'),
        TagResult.proj_id.label('proj_id'),
        TagResult.task_id.label('task_id'),
        TagResult.tag_status.label('tag_status'),
        TagResult.label_text.label('label_text'),
        TagResult.label_time.label('label_time'),
        TagResult.insertion_count.label('insertion_count'),
        TagResult.sub_count.label('sub_count'),
        TagResult.delete_count.label('delete_count'),
        TagResult.wer.label('wer'),
        TagResult.person.label('person'),
        TagResult.accent.label('accent'),
        TagResult.gender.label('gender'),
        Utterance.request_id.label('request_id'),
        Utterance.url.label('utterance_url'),
        Utterance.cut_ratio.label('cut_ratio'),
        Utterance.volume.label('volume'),
        Utterance.pre_snr.label('pre_snr'),
        Utterance.latter_snr.label('latter_snr'),
        UtteranceAccess.result.label('lexical_no_symbol'),
        UtteranceAccess.real_rtf.label('real_rtf'),
    ).filter(
        TagResult.request_id == UtteranceAccess.request_id,
        TagResult.request_id == Utterance.request_id).filter_by(
        task_id=task_id)

    if form.tag_status.data:
        q = q.filter(TagResult.tag_status == form.tag_status.data)

    if column_order == 'ascending':
        if column_name == 'tag_status':
            q = q.order_by(TagResult.tag_status.asc())
        if column_name == 'wer':
            q = q.order_by(TagResult.wer.asc())
        if column_name == 'cut_ratio':
            q = q.order_by(Utterance.cut_ratio.asc())
        if column_name == 'volume':
            q = q.order_by(Utterance.volume.asc())
        if column_name == 'pre_snr':
            q = q.order_by(Utterance.pre_snr.asc())
        if column_name == 'latter_snr':
            q = q.order_by(Utterance.latter_snr.asc())
        if column_name == 'real_rtf':
            q = q.order_by(UtteranceAccess.real_rtf.asc())
    else:
        if column_name == 'tag_status':
            q = q.order_by(TagResult.tag_status.desc())
        if column_name == 'wer':
            q = q.order_by(TagResult.wer.desc())
        if column_name == 'cut_ratio':
            q = q.order_by(Utterance.cut_ratio.desc())
        if column_name == 'volume':
            q = q.order_by(Utterance.volume.desc())
        if column_name == 'pre_snr':
            q = q.order_by(Utterance.pre_snr.desc())
        if column_name == 'latter_snr':
            q = q.order_by(Utterance.latter_snr.desc())
        if column_name == 'real_rtf':
            q = q.order_by(UtteranceAccess.real_rtf.desc())

    rvs = pager(q, page=cur_page, per_page=per_page)

    vms = []
    for rv in rvs.items:
        rv_dict = {c: getattr(rv, c, None) for c in rv._fields}
        rv_dict['uttr_url'] = current_app.config['UTTERANCE_FILE_SERVER'] + rv_dict['utterance_url']
        vms.append(rv_dict)
    return PageResultSuccess(msg=u'标注语句列表', data=vms, page=rvs.page_view())


@api.route('/list-new', methods=['POST'])
@auth.login_required
def tagresult_list_new():
    page_form = PageForm().validate_for_api()
    cur_page = page_form.page.data if page_form.page.data else 1
    per_page = page_form.limit.data if page_form.limit.data else current_app.config['DEFAULT_LISTNUM_PER_PAGE']
    task_id = TagTaskIDForm().validate_for_api().task_id.data
    form = TagResultSearchForm().validate_for_api()

    q = db_v1.session.query(TagResult, Utterance).filter(
        TagResult.is_deleted == 0,
        TagResult.request_id == Utterance.request_id,
        TagResult.task_id == task_id,
    )

    if form.tag_status.data:
        q = q.filter(TagResult.tag_status == form.tag_status.data)

    rvs = pager(q, page=cur_page, per_page=per_page)

    vms = []
    for tag_result, uttr in rvs.items:
        vm = TagResultViewListItem()._asdict()
        vm = dict(zip(vm.keys(), [dict(vm, **tag_result)[x] for x in vm.keys()]))
        vm['uttr_url'] = current_app.config['UTTERANCE_FILE_SERVER'] + uttr.url
        # vm['lexical_no_symbol'] = lexical_no_symbol
        vms.append(vm)
    request_ids = list(set([vm['request_id'] for vm in vms]))
    uttr_access_list = db_v1.session.query(UtteranceAccess).filter(
        UtteranceAccess.is_deleted == 0,
        UtteranceAccess.request_id.in_(request_ids)).all()
    uttr_access_dict = {uttr_access.request: uttr_access for uttr_access in uttr_access_list}
    for vm in vms:
        vm['lexical_no_symbol'] = getattr(uttr_access_dict[vm['request_id']], 'result', None)

    return PageResultSuccess(msg=u'标注语句列表', data=vms, page=rvs.page_view())


@api.route('/tag', methods=['POST'])
@auth.login_required
def tagresult_tag_uttrs():
    form = TagResultEditForm().validate_for_api()

    q = db_v1.session.query(TagResult, UtteranceAccess.result.label('lexical_no_symbol')).filter(
        TagResult.request_id == UtteranceAccess.request_id).filter_by(request_id=form.request_id.data)

    tagresult, lexical_no_symbol = q.first_or_404()
    with db_v1.auto_commit():
        form.populate_obj(tagresult)
        i, s, d, wer = i_s_d_wer(form.label_text.data, lexical_no_symbol)
        tagresult.insertion_count = i
        tagresult.sub_count = s
        tagresult.delete_count = d
        tagresult.wer = wer
        tagresult.tag_status = 1
        tagresult.label_time = int(time.time())

    tagtask = TagTask.query.filter_by(id=tagresult.task_id).first()
    if tagtask:
        rv = db_v1.session.query(TagResult.tag_status, func.count('*').label('cnt')).filter(
            TagResult.task_id == tagtask.id, TagResult.is_deleted == 0).group_by(TagResult.tag_status)
        tag_total = 0
        tag_cnt = 0
        for status, cnt in rv:
            tag_total += cnt
            if status == 1:
                tag_cnt += cnt

        if tag_total > 0 and tag_total == tag_cnt:
            with db_v1.auto_commit():
                tagtask.task_status = TagTaskStatusEnum.FINISHED.value
                tagtask.finish_time = int(time.time())

    return ResultSuccess(msg=u'标注成功', data={'label_time': tagresult.label_time, 'wer': tagresult.wer})


@api.route('/modify', methods=['POST'])
@auth.login_required
def tagresult_modify_uttrs():
    form = TagResultEditForm().validate_for_api()

    q = db_v1.session.query(TagResult, UtteranceAccess.result.label('lexical_no_symbol')).filter(
        TagResult.request_id == UtteranceAccess.request_id).filter_by(request_id=form.request_id.data)

    tagresult, lexical_no_symbol = q.first_or_404()
    with db_v1.auto_commit():
        form.populate_obj(tagresult)
        i, s, d, wer = i_s_d_wer(form.label_text.data, lexical_no_symbol)
        tagresult.insertion_count = i
        tagresult.sub_count = s
        tagresult.delete_count = d
        tagresult.wer = wer
        tagresult.tag_status = 1
        tagresult.label_time = int(time.time())

        # 检验该任务下
        tagtask = TagTask.query.filter_by(id=tagresult.task_id).first()

        if tagtask:
            with db_v1.auto_commit():
                tagtask.task_status = TagTaskStatusEnum.MODIFY.value

    return ResultSuccess(msg=u'修改标注成功', data={'label_time': tagresult.label_time, 'wer': tagresult.wer})


@api.route('/modifysub', methods=['POST'])
@auth.login_required
def tagresult_modify_sub():
    id = IDForm().validate_for_api().id.data
    tag_task = TagTask.query.filter_by(id=id).first()
    if tag_task:
        with db_v1.auto_commit():
            tag_task.task_status = TagTaskStatusEnum.FINISHED.value
            tag_task.finish_time = int(time.time())

    return ResultSuccess(msg=u'修改完成')
