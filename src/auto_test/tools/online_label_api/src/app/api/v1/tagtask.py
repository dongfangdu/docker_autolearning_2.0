# -*- coding: utf-8 -*-
import math
from datetime import datetime
from flask import g
from sqlalchemy import desc, and_
from sqlalchemy.orm import aliased

from app.libs.builtin_extend import namedtuple_with_defaults, datetime2timestamp
from app.libs.enums import TagTaskStatusEnum
from app.libs.error_code import DeleteSuccess, CreateSuccess, EditSuccess, PageResultSuccess, Success
from app.libs.qpaginate import pager
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db_v1
from app.models.v1.sysmng import User
from app.models.v1.tagfile import Utterance, UtteranceAccess
from app.models.v1.tagproj import TagProject, TagTask, TagResult
from app.validators.base import PageForm
from app.validators.forms_v1 import TagTaskForm, IDForm, TagTaskEditForm, TagTaskSearchForm, TagTaskUtteranceMapForm, \
    TagTaskAuditForm, TagTaskActiveForm, TagTaskIDForm, UtteranceRefSearchForm

api = Redprint('tagtask')


@api.route('', methods=['POST'])
@auth.login_required
def tagtask_add():
    form = TagTaskForm().validate_for_api()

    # 生成任务编号

    tagproject = TagProject.query.filter_by(id=form.proj_id.data).first_or_404()
    task_code_prefix = 'TTK{}'.format(str(tagproject.proj_code)[3:])

    task_code_list = TagTask.query.filter(TagTask.task_code.like(task_code_prefix + '%')).filter_by(
        with_deleted=True).all()
    task_cnt_by_code = max([int(task.task_code[-4:]) for task in task_code_list]) if len(task_code_list) > 0 else 0

    task_code = task_code_prefix + str(task_cnt_by_code + 1).zfill(4)

    tag_task = TagTask()
    with db_v1.auto_commit():
        form.populate_obj(tag_task)
        tag_task.task_code = task_code
        tag_task.create_uid = g.user.uid
        tag_task.tagging_status = 0
        tag_task.audit_status = 0

        db_v1.session.add(tag_task)

    vm = TagTaskViewListItem()._asdict()
    vm = dict(zip(vm.keys(), [dict(vm, **tag_task)[x] for x in vm.keys()]))
    create_user = User.query.filter_by(id=tag_task.create_uid).first()
    vm['creator_name'] = create_user.nickname if create_user else '-'
    tagger_user = User.query.filter_by(id=tag_task.tagger_uid).first()
    vm['tagger_name'] = tagger_user.nickname if tagger_user else '-'
    tag_project = TagProject.query.filter_by(id=tag_task.proj_id).first()
    vm['proj_code'] = tag_project.proj_code if tag_project else '-'
    vm['proj_name'] = tag_project.proj_name if tag_project else '-'

    # 标注数
    q_cnt = TagResult.query.filter_by(task_id=tag_task.id)
    cnt_all = q_cnt.count()
    q_cnt = q_cnt.filter_by(tag_status=1)
    cnt_tagged = q_cnt.count()
    # cnt_all, cnt_tagged = (0, 0)
    vm['cnt_tagged'] = cnt_tagged  # 已标注数
    vm['cnt_all'] = cnt_all  # 任务标注总数
    cumulative_rate = 0
    if cnt_all > 0:
        cumulative_rate = math.floor(cnt_tagged / cnt_all * 100)
    vm['cumulative_rate'] = cumulative_rate  # 任务进度

    return CreateSuccess(msg=u'任务新增成功', data=vm)


@api.route('/del/<int:oid>', methods=['GET'])
@auth.login_required
def tagtask_del(oid):
    with db_v1.auto_commit():
        tag_task = TagTask.query.filter_by(id=oid).first_or_404()
        tag_task.delete()
        # 任务删除后，语句的关联自动解除
        TagResult.query.filter(TagResult.task_id == oid).filter_by().update({'task_id': -1})

    return DeleteSuccess()


@api.route('/edit', methods=['POST'])
@auth.login_required
def tagtask_edit():
    id = IDForm().validate_for_api().id.data
    tag_task = TagTask.query.filter_by(id=id).first_or_404()

    form = TagTaskEditForm().validate_for_api()

    with db_v1.auto_commit():
        if form.task_name.data:
            tag_task.task_name = form.task_name.data
        # if form.proj_id.data:
        #     tag_task.proj_id = form.proj_id.data
        # if form.finish_time.data:
        #     tag_task.finish_time = form.finish_time.data
        if form.tagger_uid.data:
            tag_task.tagger_uid = form.tagger_uid.data
        # tag_task.tagging_status = 0
        # tag_task.audit_status = 0

    return EditSuccess(msg=u'任务修改成功')


@api.route('/audit', methods=['POST'])
@auth.login_required
def tagtask_audit():
    id = IDForm().validate_for_api().id.data
    tag_task = TagTask.query.filter_by(id=id).first_or_404()

    form = TagTaskAuditForm().validate_for_api()

    task_status = None
    if form.audit_status.data == 0:
        task_status = TagTaskStatusEnum.AUDITED_FAILED.value
    if form.audit_status.data == 1:
        task_status = TagTaskStatusEnum.AUDITED_SUCCESS.value

    with db_v1.auto_commit():
        if tag_task:
            tag_task.task_status = task_status
    return EditSuccess(msg=u'任务审核操作成功')


@api.route('/active', methods=['POST'])
@auth.login_required
def tagtask_active():
    id = IDForm().validate_for_api().id.data
    tag_task = TagTask.query.filter_by(id=id).first_or_404()

    form = TagTaskActiveForm().validate_for_api()

    task_status = None
    if form.active_status.data == 0:
        task_status = TagTaskStatusEnum.INACTIVED.value
    if form.active_status.data == 1:
        task_status = TagTaskStatusEnum.ONGONING.value

    with db_v1.auto_commit():
        if tag_task:
            tag_task.task_status = task_status
    return EditSuccess(msg=u'任务激活操作成功')


TagTaskViewListItemFields = (
    'create_time', 'id', 'task_code', 'task_name', 'proj_id', 'finish_time', 'create_uid', 'tagger_uid', 'task_status')
TagTaskViewListItem = namedtuple_with_defaults('TagTaskViewListItem', TagTaskViewListItemFields,
                                               default_values=(None,) * len(TagTaskViewListItemFields))


@api.route('/list', methods=['POST'])
@auth.login_required
def tagtask_list():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    form = TagTaskSearchForm().validate_for_api()
    CreateUser = aliased(User)
    TaggerUser = aliased(User)
    OmUser = aliased(User)
    scope = g.user.scope
    # 权限过滤
    create_user_id = None
    tagger_user_id = None
    om_user_id = None
    is_outer_join = True
    if scope == 'taskmanger':
        create_user_id = g.user.uid

    if scope == 'taskoperator':
        is_outer_join = False
        tagger_user_id = g.user.uid
    if scope == 'supervisor':
        om_user_id = g.user.uid

    if scope == 'supervisor':
        q = db_v1.session.query(TagTask, OmUser).order_by(TagTask.create_time.desc()).filter(
            TagTask.create_uid == OmUser.id,
        )
    else:
        q = db_v1.session.query(TagTask, TagProject, CreateUser).order_by(TagTask.create_time.desc()).filter(
        TagTask.create_uid == CreateUser.id,
        TagTask.proj_id == TagProject.id).add_entity(TaggerUser).join(TaggerUser, TagTask.tagger_uid == TaggerUser.id,
                                                                      isouter=is_outer_join)
    if form.create_time_left.data:
        q = q.filter(TagTask.create_time >= form.create_time_left.data)
    if form.create_time_right.data:
        q = q.filter(TagTask.create_time <= form.create_time_right.data)
    if form.proj_code.data:
        q = q.filter(TagProject.proj_code.like('%' + form.proj_code.data + "%"))
    if form.task_code.data:
        q = q.filter(TagTask.task_code.like('%' + form.task_code.data + "%"))
    if form.tagger_name.data:
        q = q.filter(TaggerUser.nickname.like('%' + form.tagger_name.data + "%"))
    # if form.tagging_status.data:
    #     q = q.filter(TagTask.tagging_status == form.tagging_status.data)
    # if form.audit_status.data:
    #     q = q.filter(TagTask.audit_status == form.audit_status.data)
    if form.task_status.data !='':
        q = q.filter(TagTask.task_status == form.task_status.data)

    if create_user_id:
        q = q.filter(CreateUser.id == create_user_id)
    if tagger_user_id:
        q = q.filter(TaggerUser.id == tagger_user_id)
        q = q.filter(TagTask.task_status != 0)
    if om_user_id:
        q = q.filter(OmUser.id == om_user_id)
    q = q.filter(TagTask.is_deleted == 0)
    rvs = pager(q, page=cur_page, per_page=per_page)

    vms = []
    if scope == 'supervisor':
        for tag_task, om_user in rvs.items:
            vm = TagTaskViewListItem()._asdict()
            vm = dict(zip(vm.keys(), [dict(vm, **tag_task)[x] for x in vm.keys()]))
            vm['creator_name'] = om_user.nickname
            vm['tagger_name'] = om_user.nickname if om_user else '-'

            # 标注数
            q_cnt = TagResult.query.filter_by(task_id=tag_task.id)
            cnt_all = q_cnt.count()
            q_cnt = q_cnt.filter_by(tag_status=1)
            cnt_tagged = q_cnt.count()
            # cnt_all, cnt_tagged = (0, 0)
            vm['cnt_tagged'] = cnt_tagged  # 已标注数
            vm['cnt_all'] = cnt_all  # 任务标注总数
            cumulative_rate = 0
            if tag_task.task_status != 0 and cnt_all > 0:
                cumulative_rate = math.floor(float(cnt_tagged) / cnt_all * 100)
            vm['cumulative_rate'] = cumulative_rate  # 任务进度
            vms.append(vm)
    else:
        for tag_task, tag_project, create_user, tagger_user in rvs.items:
            vm = TagTaskViewListItem()._asdict()
            vm = dict(zip(vm.keys(), [dict(vm, **tag_task)[x] for x in vm.keys()]))
            vm['creator_name'] = create_user.nickname
            vm['tagger_name'] = tagger_user.nickname if tagger_user else '-'
            vm['proj_code'] = tag_project.proj_code
            vm['proj_name'] = tag_project.proj_name

            # 标注数
            q_cnt = TagResult.query.filter_by(task_id=tag_task.id)
            cnt_all = q_cnt.count()
            q_cnt = q_cnt.filter_by(tag_status=1)
            cnt_tagged = q_cnt.count()
            # cnt_all, cnt_tagged = (0, 0)
            vm['cnt_tagged'] = cnt_tagged  # 已标注数
            vm['cnt_all'] = cnt_all  # 任务标注总数
            cumulative_rate = 0
            if tag_task.task_status != 0 and cnt_all > 0:
                cumulative_rate = math.floor(float(cnt_tagged) / cnt_all * 100)
            vm['cumulative_rate'] = cumulative_rate  # 任务进度

            vms.append(vm)

    return PageResultSuccess(msg=u'任务列表', data=vms, page=rvs.page_view())


@api.route('/info-uttrs', methods=['POST'])
@auth.login_required
def tagtask_info_utterance():
    # TODO
    id = IDForm().validate_for_api().id.data

    CreateUser = aliased(User)
    TaggerUser = aliased(User)
    tag_task, tag_project, create_user, tagger_user = db_v1.session.query(TagTask, TagProject, CreateUser,
                                                                          TaggerUser).filter(
        TagTask.tagger_uid == TaggerUser.id,
        TagTask.create_uid == CreateUser.id,
        TagTask.proj_id == TagProject.id).filter_by(id=id).first_or_404()

    vm = TagTaskViewListItem()._asdict()
    vm = dict(zip(vm.keys(), [dict(vm, **tag_task)[x] for x in vm.keys()]))
    vm['proj_code'] = tag_project.proj_code
    vm['creator_name'] = create_user.nickname
    vm['tagger_name'] = tagger_user.rname
    # TODO
    # 任务进度
    cnt_total, cnt_finished = (0, 0)
    vm['cnt_total'] = cnt_total
    vm['cnt_finished'] = cnt_finished
    vm['cnt_unfinished'] = cnt_total - cnt_finished
    vm['cumulative_rate'] = '-' if cnt_total == 0 else cnt_total

    return PageResultSuccess(msg=u'任务详情', data=vm)


@api.route('/list-uttrs', methods=['POST'])
@auth.login_required
def tagtask_list_utterance():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    form = IDForm().validate_for_api()
    id = form.id.data

    q = db_v1.session.query(TagResult, Utterance, UtteranceAccess.time.label('stt_time'),
                            UtteranceAccess.result.label('lexical_no_symbol'), ).filter(
        TagResult.request_id == Utterance.request_id,
        TagResult.request_id == UtteranceAccess.request_id).filter_by(task_id=id)

    if form.tag_status.data is not None and form.tag_status.data != '':
        q = q.filter(and_(TagResult.tag_status == form.tag_status.data, Utterance.is_assigned == 1))
    if form.stt_time_left.data and form.stt_time_left.data != '':
        q = q.filter(UtteranceAccess.time >= datetime.fromtimestamp(form.stt_time_left.data))
    if form.stt_time_right.data and form.stt_time_right.data != '':
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
        vm['lexical_no_symbol'] = rv_dict['lexical_no_symbol']
        vm['tag_status'] = rv_dict['tag_result_tag_status']
        vm['wer'] = rv_dict['tag_result_wer']
        vms.append(vm)

    return PageResultSuccess(msg=u'任务关联语句列表', data=vms, page=rvs.page_view())


@api.route('/set-all-uttrs', methods=['POST'])
@auth.login_required
def tagtask_set_all_utterance():
    task_id = TagTaskIDForm().validate_for_api().task_id.data
    tag_task = TagTask.query.filter_by(id=task_id).first_or_404()
    form = UtteranceRefSearchForm().validate_for_api()

    q = db_v1.session.query(TagResult).filter(
        TagResult.request_id == UtteranceAccess.request_id).filter(
        TagResult.task_id == -1, TagResult.proj_id == tag_task.proj_id, TagResult.is_deleted == 0)

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

    with db_v1.auto_commit():
        for tag_result in q.all():
            tag_result.task_id = task_id

    return Success(msg=u'任务语句关联成功')


@api.route('/set-uttrs', methods=['POST'])
@auth.login_required
def tagtask_set_utterance():
    form = TagTaskUtteranceMapForm().validate_for_api()

    req_id_list = form.req_id_list.data

    tagtask = TagTask.query.filter_by(id=form.task_id.data).first_or_404()

    with db_v1.auto_commit():
        tag_result_objs = TagResult.query.filter(TagResult.proj_id == tagtask.proj_id,
                                                 TagResult.request_id.in_(req_id_list)).filter_by().all()
        for q in tag_result_objs:
            q.task_id = tagtask.id

    return Success(msg=u'任务语句关联成功')


@api.route('/del-uttrs', methods=['POST'])
@auth.login_required
def tagtask_del_utterance():
    form = TagTaskUtteranceMapForm().validate_for_api()
    req_id_list = form.req_id_list.data

    if len(req_id_list) > 0:
        with db_v1.auto_commit():
            tag_result_objs = TagResult.query.filter(TagResult.task_id == form.task_id.data,
                                                    TagResult.request_id.in_(req_id_list)).filter_by().all()
            for q in tag_result_objs:
                q.task_id = -1

    return Success(msg=u'任务语句解联成功')

@api.route('/del-all-uttrs', methods=['POST'])
@auth.login_required
def tagtask_del_all_utterance():
    form = IDForm().validate_for_api()
    id = form.id.data

    q = db_v1.session.query(TagResult, Utterance, UtteranceAccess.time.label('stt_time')).filter(
        TagResult.request_id == Utterance.request_id, TagResult.request_id == UtteranceAccess.request_id).filter_by( task_id=id )

    if form.tag_status.data is not None and form.tag_status.data != '':
        q = q.filter(and_(TagResult.tag_status == form.tag_status.data, Utterance.is_assigned == 1))
    if form.stt_time_left.data and form.stt_time_right.data != '':
        q = q.filter(UtteranceAccess.time >= datetime.fromtimestamp(form.stt_time_left.data))
    if form.stt_time_right.data and form.stt_time_right.data != '':
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

    q_final = []
    for row in q.all():
        q_final.append(row[0])
    with db_v1.auto_commit():
        for v in q_final:
            v.task_id = -1

    return Success(msg=u'任务全部语句解联成功')
