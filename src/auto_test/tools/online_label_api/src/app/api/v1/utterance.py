# -*- coding: utf-8 -*-
from datetime import datetime
from flask import request
from sqlalchemy import and_, or_, desc
from sqlalchemy.sql import label

from app.libs.builtin_extend import datetime2timestamp
from app.libs.error_code import PageResultSuccess, ResultSuccess, ParameterException
from app.libs.qpaginate import pager
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db_v1
from app.models.v1.tagfile import Utterance, UtteranceTrace, UtteranceAccess
from app.models.v1.tagproj import TagProject, TagTask, TagResult
from app.validators.base import PageForm
from app.validators.forms_v1 import UtteranceSearchForm, TagTaskIDForm, UtteranceRefSearchForm, UtteranceCalcForm

api = Redprint('uttr')


@api.route('/list-unref-proj', methods=['POST'])
@auth.login_required
def utterance_list_unref_project():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    form = UtteranceRefSearchForm().validate_for_api()

    q = db_v1.session.query(Utterance, UtteranceAccess.time.label('stt_time'),
                            UtteranceAccess.result.label('lexical_no_symbol'),
                            UtteranceAccess.detect_duration.label('detect_duration')).filter(
        Utterance.request_id == UtteranceAccess.request_id,
        Utterance.is_deleted == 0, Utterance.is_assigned == 0)

    if form.stt_time_left.data:
        q = q.filter(UtteranceAccess.time >= datetime.fromtimestamp(form.stt_time_left.data))
    if form.stt_time_right.data:
        q = q.filter(UtteranceAccess.time <= datetime.fromtimestamp(form.stt_time_right.data))

    if form.num1.data is not None and form.num1.data != '':
        num_left = int(form.num1.data) - 1
        if form.num2.data is not None and form.num2.data != '':
            num_right = int(form.num2.data) - int(form.num1.data) + 1
            q = q.order_by(desc(UtteranceAccess.time)).limit(num_right).offset(num_left)
        else:
            q = q.order_by(desc(UtteranceAccess.time)).offset(num_left)
    else:
        if form.num2.data is not None and form.num2.data != '':
            num_right = int(form.num2.data)
            q = q.order_by(desc(UtteranceAccess.time)).limit(num_right)
        else:
            q = q.order_by(desc(UtteranceAccess.time))
    q_final = db_v1.session.query(q.subquery('inner_q', with_labels=True))
    rvs = pager(q_final, page=cur_page, per_page=per_page)

    vms = []
    for rv in rvs.items:
        rv_dict = {c: getattr(rv, c, None) for c in rv._fields}
        vm = {}
        vm['request_id'] = rv_dict['utterance_request_id']
        vm['stt_time'] = datetime2timestamp(rv_dict['stt_time'])
        vm['detect_duration'] = rv_dict['detect_duration']
        vms.append(vm)

    return PageResultSuccess(msg=u'未关联项目的语句列表', data=vms, page=rvs.page_view())


@api.route('/list-unref-task', methods=['POST'])
@auth.login_required
def utterance_list_unref_task():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    task_id = TagTaskIDForm().validate_for_api().task_id.data
    tag_task = TagTask.query.filter_by(id=task_id).first_or_404()

    form = UtteranceRefSearchForm().validate_for_api()

    q = db_v1.session.query(Utterance, UtteranceAccess.time.label('stt_time'),
                            UtteranceAccess.result.label('lexical_no_symbol'),
                            UtteranceAccess.detect_duration.label('detect_duration')).filter(
        Utterance.request_id == UtteranceAccess.request_id, TagResult.request_id == Utterance.request_id).filter(
        TagResult.task_id == -1, TagResult.proj_id == tag_task.proj_id, TagResult.is_deleted == 0,
        Utterance.is_deleted == 0)

    if form.stt_time_left.data:
        q = q.filter(UtteranceAccess.time >= datetime.fromtimestamp(form.stt_time_left.data))
    if form.stt_time_right.data:
        q = q.filter(UtteranceAccess.time <= datetime.fromtimestamp(form.stt_time_right.data))
    if form.num1.data is not None and form.num1.data != '':
        num_left = int(form.num1.data) - 1
        if form.num2.data is not None and form.num2.data != '':
            num_right = int(form.num2.data) - int(form.num1.data) + 1
            q = q.order_by(desc(UtteranceAccess.time)).limit(num_right).offset(num_left)
        else:
            q = q.order_by(desc(UtteranceAccess.time)).offset(num_left)
    else:
        if form.num2.data is not None and form.num2.data != '':
            num_right = int(form.num2.data)
            q = q.order_by(desc(UtteranceAccess.time)).limit(num_right)
        else:
            q = q.order_by(desc(UtteranceAccess.time))

    q_final = db_v1.session.query(q.subquery('inner_q', with_labels=True))
    rvs = pager(q_final, page=cur_page, per_page=per_page)
    vms = []
    for rv in rvs.items:
        rv_dict = {c: getattr(rv, c, None) for c in rv._fields}
        vm = {}
        # vm['request_id'] = rv_dict['Utterance'].request_id
        vm['request_id'] = rv_dict['utterance_request_id']
        vm['stt_time'] = datetime2timestamp(rv_dict['stt_time'])
        vm['detect_duration'] = rv_dict['detect_duration']
        vms.append(vm)

    return PageResultSuccess(msg=u'未关联任务的语句列表', data=vms, page=rvs.page_view())


@api.route('/list', methods=['POST'])
@auth.login_required
def utterance_list():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    form = UtteranceSearchForm().validate_for_api()

    is_outer_join = True
    if form.tag_status.data is not None and form.tag_status.data != '':
        is_outer_join = False

    proj_ids = None
    if form.proj_code.data and form.proj_code.data != '':
        is_outer_join = False
        proj_rvs = db_v1.session.query(TagProject.id).filter(
            TagProject.proj_code.like('%' + form.proj_code.data + "%")).filter_by().all()
        proj_ids = [proj_id for proj_id, in proj_rvs]

    task_ids = None
    if form.task_code.data and form.task_code.data != '':
        is_outer_join = False
        task_rvs = db_v1.session.query(TagTask.id).filter(
            TagTask.task_code.like('%' + form.task_code.data + "%")).filter_by().all()
        task_ids = [task_id for task_id, in task_rvs]

    sub_q = db_v1.session.query(TagResult.id.label('tag_result_id'),
                                TagResult.request_id.label('request_id'),
                                TagResult.is_deleted.label('tag_result_is_deleted'),
                                TagResult.tag_status.label('tag_status'),
                                TagResult.task_id.label('task_id'),
                                TagResult.proj_id.label('proj_id'),
                                TagResult.wer.label('wer'),
                                TagResult.label_text.label('label_text'), )\
        .filter(TagResult.is_deleted == 0).subquery('sub_q')
    q = db_v1.session.query(Utterance.request_id.label('request_id'),
                            Utterance.cut_ratio.label('cut_ratio'),
                            Utterance.volume.label('volume'),
                            Utterance.snr.label('snr'),
                            UtteranceAccess.time.label('stt_time'),
                            UtteranceAccess.result.label('lexical_no_symbol'),
                            UtteranceAccess.real_rtf.label('real_rtf'),
                            sub_q.c.tag_result_id.label('tag_result_id'),
                            sub_q.c.tag_result_is_deleted.label('tag_result_is_deleted'),
                            sub_q.c.tag_status.label('tag_status'),
                            sub_q.c.task_id.label('task_id'),
                            sub_q.c.proj_id.label('proj_id'),
                            sub_q.c.label_text.label('label_text'),
                            ).filter(Utterance.request_id == UtteranceAccess.request_id).join(
        sub_q, sub_q.c.request_id == Utterance.request_id, isouter=is_outer_join).filter(
        Utterance.is_deleted == 0,  UtteranceAccess.is_deleted == 0)

    if proj_ids is not None:
        if len(proj_ids) == 0:
            page_view_item = {'page': cur_page, 'limit': per_page, 'total': 0}
            return PageResultSuccess(msg=u'语句管理列表', data=[], page=page_view_item)
        # TODO 用别的方法取代in
        q = q.filter(sub_q.c.proj_id.in_(proj_ids))
    if task_ids is not None:
        if len(task_ids) == 0:
            page_view_item = {'page': cur_page, 'limit': per_page, 'total': 0}
            return PageResultSuccess(msg=u'语句管理列表', data=[], page=page_view_item)
        # TODO 用别的方法取代in
        q = q.filter(sub_q.c.task_id.in_(task_ids))

    if form.tag_status.data is not None and form.tag_status.data != '':
        if form.tag_status.data == 0:
            q = q.filter(or_(sub_q.c.tag_status == form.tag_status.data, Utterance.is_assigned == 0))
        else:
            q = q.filter(and_(sub_q.c.tag_status == form.tag_status.data, Utterance.is_assigned == 1))
    if form.stt_time_left.data and form.stt_time_left.data != '':
        q = q.filter(UtteranceAccess.time >= datetime.fromtimestamp(form.stt_time_left.data))
    if form.stt_time_right.data and form.stt_time_right.data != '':
        q = q.filter(UtteranceAccess.time <= datetime.fromtimestamp(form.stt_time_right.data))
    q = q.order_by(UtteranceAccess.time.desc())
    print q
    rvs = pager(q, page=cur_page, per_page=per_page)
    project_info = TagProject.query.filter_by().all()
    project_info = {tag_project.id: tag_project for tag_project in project_info}

    task_info = TagTask.query.filter_by().all()
    task_info = {tag_task.id: tag_task for tag_task in task_info}
    vms = []
    for rv in rvs.items:
        rv_dict = {c: getattr(rv, c, None) for c in rv._fields}
        vm = {}
        vm['request_id'] = rv_dict['request_id']
        vm['stt_time'] = datetime2timestamp(rv_dict['stt_time'])
        vm['lexical_no_symbol'] = rv_dict['lexical_no_symbol']
        vm['real_rft'] = rv_dict['real_rtf']
        vm['cut_ratio'] = rv_dict['cut_ratio']
        vm['volume'] = rv_dict['volume']
        vm['snr'] = rv_dict['snr']
        if rv_dict.get('tag_result_id') and rv_dict['tag_result_is_deleted'] == 0:
            vm['label_text'] = rv_dict['label_text']
            vm['tag_status'] = rv_dict['tag_status']
            vm['proj_name'] = project_info[rv_dict['proj_id']].proj_name
            vm['proj_code'] = project_info[rv_dict['proj_id']].proj_code
            if task_info.get(rv_dict['task_id']):
                vm['task_name'] = task_info.get(rv_dict['task_id']).task_name
                vm['task_code'] = task_info.get(rv_dict['task_id']).task_code
            else:
                vm['task_name'] = ''  # rv_dict['task_name']
                vm['task_code'] = ''  # rv_dict['task_code']
        else:
            vm['wer'] = 0
            vm['label_text'] = ''
            vm['tag_status'] = 0
            vm['proj_name'] = ''  # rv_dict['proj_name']
            vm['proj_code'] = ''  # rv_dict['proj_code']
            vm['task_name'] = ''  # rv_dict['task_name']
            vm['task_code'] = ''  # rv_dict['task_code']
        vms.append(vm)

    return PageResultSuccess(msg=u'语句管理列表', data=vms, page=rvs.page_view())


@api.route('/list-old', methods=['POST'])
@auth.login_required
def utterance_search():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    form = UtteranceSearchForm().validate_for_api()

    reg_info_1 = db_v1.session.query(label('request_id', UtteranceTrace.request_id),
                                     label('stt_time', UtteranceTrace.time),
                                     label('lexical_no_symbol', UtteranceTrace.result),
                                     label('detect_duration', UtteranceTrace.detect_duration),
                                     label('real_rtf', UtteranceTrace.real_rtf))
    reg_info_2 = db_v1.session.query(label('request_Id', UtteranceAccess.request_id),
                                     label('stt_time', UtteranceAccess.time),
                                     label('lexical_no_symbol', UtteranceAccess.result),
                                     label('detect_duration', UtteranceAccess.detect_duration),
                                     label('real_rtf', UtteranceAccess.real_rtf))
    UtteranceRegInfo = reg_info_1.union_all(reg_info_2).subquery('reg_info')

    is_outer_join_1, is_outer_join_2 = True, True

    condition1 = True
    if form.proj_code.data and form.proj_code.data != '':
        condition1 = and_(condition1, TagProject.proj_code.like('%' + form.proj_code.data + "%"))
        is_outer_join_2 = False
    if form.task_code.data and form.task_code.data != '':
        condition1 = and_(condition1, TagTask.task_code.like('%' + form.task_code.data + "%"))
        is_outer_join_1 = False
        is_outer_join_2 = False
    if form.tag_status.data is not None and form.tag_status.data != '':
        condition1 = and_(condition1, TagResult.tag_status == form.tag_status.data)
        is_outer_join_2 = False
        is_outer_join_1 = False
    condition1 = and_(condition1, TagResult.is_deleted == 0)

    condition2 = (Utterance.request_id is not None)
    if form.stt_time_left.data and form.stt_time_left.data != '':
        condition2 = and_(condition2, UtteranceRegInfo.c.stt_time >= datetime.fromtimestamp(form.stt_time_left.data))
    if form.stt_time_right.data and form.stt_time_right.data != '':
        condition2 = and_(condition2, UtteranceRegInfo.c.stt_time <= datetime.fromtimestamp(form.stt_time_right.data))
    condition2 = and_(condition2, Utterance.is_deleted == 0)

    # 第一个必须是TagResult.request_id
    sub_q = db_v1.session.query(
        TagResult.request_id, TagResult.label_text, TagResult.wer, TagResult.tag_status, TagProject.proj_name,
        TagProject.proj_code, TagTask.task_name,
        TagTask.task_code
    ).filter(
        TagResult.proj_id == TagProject.id
    ).join(
        TagTask, TagResult.task_id == TagTask.id, isouter=is_outer_join_1
    ).filter(condition1).subquery('sub_q')

    query_res_objs = db_v1.session.query(
        Utterance, UtteranceRegInfo, sub_q
    ).filter(
        Utterance.request_id == UtteranceRegInfo.c.request_id
    ).join(
        sub_q, sub_q.c.request_id == Utterance.request_id, isouter=is_outer_join_2
    ).filter(condition2)

    rvs = pager(query_res_objs, page=cur_page, per_page=per_page)
    vms = []
    for objs in rvs.items:
        vm = {}
        vm['request_id'] = objs[0].request_id
        vm['stt_time'] = datetime2timestamp(objs[2])
        vm['lexical_no_symbol'] = objs[3]
        vm['label_text'] = objs[7]
        vm['wer'] = objs[8]
        vm['real_rft'] = objs[5]
        vm['cut_ratio'] = objs[0].cut_ratio
        vm['volume'] = objs[0].volume
        vm['snr'] = objs[0].snr
        vm['tag_status'] = objs[9]
        vm['proj_name'] = objs[10]
        vm['proj_code'] = objs[11]
        vm['task_name'] = objs[12]
        vm['task_code'] = objs[13]
        vms.append(vm)

    return PageResultSuccess(msg=u'语句管理列表', data=vms, page=rvs.page_view())


@api.route('/list-debug', methods=['POST'])
@auth.login_required
def utterance_search_debug():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    form = UtteranceSearchForm().validate_for_api()

    reg_info_1 = db_v1.session.query(label('request_id', UtteranceTrace.request_id),
                                     label('stt_time', UtteranceTrace.time),
                                     label('lexical_no_symbol', UtteranceTrace.result),
                                     label('detect_duration', UtteranceTrace.detect_duration),
                                     label('real_rtf', UtteranceTrace.real_rtf))
    reg_info_2 = db_v1.session.query(label('request_Id', UtteranceAccess.request_id),
                                     label('stt_time', UtteranceAccess.time),
                                     label('lexical_no_symbol', UtteranceAccess.result),
                                     label('detect_duration', UtteranceAccess.detect_duration),
                                     label('real_rtf', UtteranceAccess.real_rtf))
    UtteranceRegInfo = reg_info_1.union_all(reg_info_2).subquery('reg_info')

    is_outer_join_1, is_outer_join_2 = True, True

    condition1 = True
    if form.proj_code.data:
        condition1 = and_(condition1, TagProject.proj_code.like('%' + form.proj_code.data + "%"))
        is_outer_join_2 = False
    if form.task_code.data:
        condition1 = and_(condition1, TagTask.task_code.like('%' + form.task_code.data + "%"))
        is_outer_join_1 = False
        is_outer_join_2 = False
    if form.tag_status.data is not None:
        condition1 = and_(condition1, TagResult.tag_status == form.tag_status.data)
        is_outer_join_2 = False
        is_outer_join_1 = False
    condition1 = and_(condition1, TagResult.is_deleted == 0)

    condition2 = (Utterance.request_id is not None)
    if form.stt_time_left.data:
        condition2 = and_(condition2, UtteranceRegInfo.c.stt_time >= datetime.fromtimestamp(form.stt_time_left.data))
    if form.stt_time_right.data:
        condition2 = and_(condition2, UtteranceRegInfo.c.stt_time <= datetime.fromtimestamp(form.stt_time_right.data))
    condition2 = and_(condition2, Utterance.is_deleted == 0)

    # 第一个必须是TagResult.request_id
    sub_q = db_v1.session.query(
        TagResult.request_id, TagResult.label_text, TagResult.wer, TagResult.tag_status, TagProject.proj_name,
        TagProject.proj_code, TagTask.task_name,
        TagTask.task_code
    ).filter(
        TagResult.proj_id == TagProject.id
    ).join(
        TagTask, TagResult.task_id == TagTask.id, isouter=is_outer_join_1
    ).filter(condition1).subquery('sub_q')

    query_res_objs = db_v1.session.query(
        Utterance, UtteranceRegInfo, sub_q
    ).filter(
        Utterance.request_id == UtteranceRegInfo.c.request_id
    ).join(
        sub_q, sub_q.c.request_id == Utterance.request_id, isouter=is_outer_join_2
    ).filter(condition2)

    rvs = pager(query_res_objs, page=cur_page, per_page=per_page)
    vms = []

    for objs in rvs.items:
        vm = {}
        vm['request_id'] = objs[0].request_id
        vm['stt_time'] = datetime2timestamp(objs[2])
        vm['lexical_no_symbol'] = objs[3]
        vm['label_text'] = objs[7]
        vm['wer'] = objs[8]
        vm['real_rft'] = objs[5]
        vm['cut_ratio'] = objs[0].cut_ratio
        vm['volume'] = objs[0].volume
        vm['snr'] = objs[0].snr
        vm['tag_status'] = objs[9]
        vm['proj_name'] = objs[10]
        vm['proj_code'] = objs[11]
        vm['task_name'] = objs[12]
        vm['task_code'] = objs[13]
        vms.append(vm)

    return PageResultSuccess(msg=u'语句管理列表', data=vms, page=rvs.page_view())


@api.route('/calc-wer', methods=['POST'])
@auth.login_required
def calculate_wer():
    """
    计算被选语句中已标注语句的错误率. 若选中的语句均未标注,返回语句未标注的提示/异常.
    """
    data = request.get_json()
    request_ids = data.get('req_id_list')

    form = UtteranceCalcForm().validate_for_api()
    is_calc_all = form.is_calc_all.data

    if not (is_calc_all == 1):
        # 没有数据传入
        if not request_ids and len(request_ids) < 1:
            raise ParameterException(msg=u'未选中任何语句')

    q = db_v1.session.query(
        TagResult.insertion_count, TagResult.sub_count, TagResult.delete_count, TagResult.label_text
    ).filter(TagResult.tag_status != 0)

    if not (is_calc_all == 1):
        q = q.filter(TagResult.request_id.in_(request_ids))

    query_results = q.all()

    if not query_results:
        raise ParameterException(msg=u'选中的语句均未标注')

    # calc wer
    i, s, d, c = [0] * 4
    for item in query_results:
        i += item[0] or 0
        s += item[1] or 0
        d += item[2] or 0
        c += len(item[-1] or '')
    wer = 100
    if c != 0:
        wer = float(i + s + d) / c * 100
    return ResultSuccess(msg=u'错误率计算成功', data={'wer': round(wer, 2)})
