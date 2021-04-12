# -*- coding: utf-8 -*-
import logging

import math
from datetime import datetime
from flask import g, current_app, request
from sqlalchemy import desc, or_
from sqlalchemy.orm import aliased

from app.libs.builtin_extend import namedtuple_with_defaults, datetime2timestamp, current_timestamp_sec
from app.libs.enums import LabelTaskStatusEnum, LabelUserMapRelTypeEnum, LabelTaskAuditStatusEnum, \
    LabelTaskActiveStatusEnum, LabelResultStatusEnum, UtteranceStatusEnum, ChoicesExTypeEnum, ChoicesExItemEnum
from app.libs.error_code import DeleteSuccess, CreateSuccess, EditSuccess, PageResultSuccess, Success, \
    ParameterException, ResultSuccess
from app.libs.qpaginate import pager
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db_v2
from app.models.v2.engine.ng import NgDiting, NgDitingRelation
from app.models.v2.engine.utterance import UtteranceAudio, UtteranceAccess
from app.models.v2.web.label import LabelProject, LabelTask, LabelResult, LabelUserMap, LabelUtteranceInfo, LabelDitingInfo
from app.models.v2.web.sysmgr import User, Role
from app.validators.base import PageForm, ColumnSortForm
from app.validators.forms_v2 import LabelTaskForm, IDForm, LabelTaskEditForm, LabelTaskSearchForm, \
    LabelTaskUtteranceMapForm, LabelTaskAuditForm, LabelTaskActiveForm, LabelTaskIDForm, UtteranceRefSearchForm, \
    UtteranceSearchForm, LabelTaskAddSVForm, UtteranceIDListForm, UtteranceSVSearchForm

api = Redprint('lbtask')
logger = logging.getLogger(__name__)


@api.route('', methods=['POST'])
@auth.login_required
def lbtask_add():
    form = LabelTaskForm().validate_for_api()

    # 生成任务编号
    label_project = LabelProject.query.filter_by(id=form.proj_id.data).first_or_404()
    task_code_prefix = '{}{}'.format(current_app.config['BUSI_LBTASK_CODE_PREFIX'], str(label_project.proj_code)[3:])

    placeholder_num = current_app.config['BUSI_LBTASK_CODE_PLACEHOLDER_NUM']
    task_code_list = LabelTask.query.with_entities(LabelTask.task_code).filter(
        LabelTask.task_code.like(task_code_prefix + '%')).filter_by(
        with_deleted=True).all()
    task_cnt_by_code = max(
        [int(task_code[-min(placeholder_num, len(task_code) - len(task_code_prefix)):]) for task_code, in
         task_code_list]) if len(
        task_code_list) > 0 else 0
    task_code = task_code_prefix + str(task_cnt_by_code + 1).zfill(placeholder_num)

    label_task = LabelTask()
    with db_v2.auto_commit():
        form.populate_obj(label_task)
        label_task.task_code = task_code
        label_task.create_uid = g.user.uid
        label_task.create_time = current_timestamp_sec()
        label_task.task_status = LabelTaskStatusEnum.INACTIVED.value

        db_v2.session.add(label_task)

    # 标注人员与标注任务关系录入
    if form.tagger_uids.data and len(form.tagger_uids.data) > 0:
        with db_v2.auto_commit():
            label_user_map_list = []
            for tagger_uid in form.tagger_uids.data:
                label_task_user_map = LabelUserMap()
                label_task_user_map.rel_id = label_task.id
                label_task_user_map.rel_type = LabelUserMapRelTypeEnum.TASK.value
                label_task_user_map.uid = tagger_uid
                label_user_map_list.append(label_task_user_map)

            db_v2.session.bulk_save_objects(label_user_map_list)

    vm = LabelTaskViewListItem()._asdict()
    vm = dict(zip(vm.keys(), [dict(vm, **label_task)[x] for x in vm.keys()]))
    create_user = User.query.filter_by(id=label_task.create_uid).first()
    vm['creator_name'] = create_user.nickname if create_user else '-'
    # tagger_user = User.query.filter_by(id=label_task.tagger_uid).first()
    # vm['tagger_name'] = tagger_user.nickname if tagger_user else '-'
    tagger_users = db_v2.session.query(User.id, User.nickname).filter(
        LabelUserMap.is_deleted == 0,
        LabelUserMap.rel_id == label_task.id,
        LabelUserMap.rel_type == LabelUserMapRelTypeEnum.TASK.value,
        LabelUserMap.uid == User.id).filter_by().all()

    vm['taggers'] = [{'uid': uid, 'name': name} for uid, name in tagger_users]

    vm['proj_code'] = label_project.proj_code if label_project else '-'
    vm['proj_name'] = label_project.proj_name if label_project else '-'

    # 标注数
    q_cnt = LabelResult.query.filter_by(task_id=label_task.id)
    cnt_all = q_cnt.count()
    q_cnt = q_cnt.filter_by(label_status=1)
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
def lbtask_del(oid):
    with db_v2.auto_commit():
        label_task = LabelTask.query.filter_by(id=oid).first_or_404()
        label_task.delete()
        # 任务删除后，语句的关联自动解除
        LabelResult.query.filter(LabelResult.task_id == oid).filter_by().update({'task_id': -1})
        LabelUserMap.query.filter(LabelUserMap.rel_id == oid,
                                  LabelUserMap.rel_type == LabelUserMapRelTypeEnum.TASK.value).filter_by().update(
            {'is_deleted': 1})

    return DeleteSuccess()


@api.route('/edit', methods=['POST'])
@auth.login_required
def lbtask_edit():
    id = IDForm().validate_for_api().id.data
    label_task = LabelTask.query.filter_by(id=id).first_or_404()

    form = LabelTaskEditForm().validate_for_api()

    if form.task_name.data:
        with db_v2.auto_commit():
            label_task.task_name = form.task_name.data
    if form.tagger_uids.data and len(form.tagger_uids.data) > 0:
        with db_v2.auto_commit():
            LabelUserMap.query.filter(LabelUserMap.rel_id == label_task.id,
                                      LabelUserMap.rel_type == LabelUserMapRelTypeEnum.TASK.value).filter_by().update(
                {'is_deleted': 1})

            label_user_map_list = []
            for tagger_uid in form.tagger_uids.data:
                label_task_user_map = LabelUserMap()
                label_task_user_map.rel_id = label_task.id
                label_task_user_map.rel_type = LabelUserMapRelTypeEnum.TASK.value
                label_task_user_map.uid = tagger_uid
                label_user_map_list.append(label_task_user_map)

            db_v2.session.bulk_save_objects(label_user_map_list)

    return EditSuccess(msg=u'任务修改成功')


@api.route('/audit', methods=['POST'])
@auth.login_required
def lbtask_audit():
    id = IDForm().validate_for_api().id.data
    label_task = LabelTask.query.filter_by(id=id).first_or_404()

    form = LabelTaskAuditForm().validate_for_api()

    task_status = None
    if form.audit_status.data == LabelTaskAuditStatusEnum.FAILED.value:
        task_status = LabelTaskStatusEnum.AUDITED_FAILED.value
    elif form.audit_status.data == LabelTaskAuditStatusEnum.SUCCESS.value:
        task_status = LabelTaskStatusEnum.AUDITED_SUCCESS.value

    with db_v2.auto_commit():
        if label_task:
            label_task.task_status = task_status
    return EditSuccess(msg=u'任务审核操作成功')


@api.route('/active', methods=['POST'])
@auth.login_required
def lbtask_active():
    id = IDForm().validate_for_api().id.data
    label_task = LabelTask.query.filter_by(id=id).first_or_404()

    form = LabelTaskActiveForm().validate_for_api()

    task_status = None
    if form.active_status.data == LabelTaskActiveStatusEnum.FROZEN.value:
        task_status = LabelTaskStatusEnum.INACTIVED.value
    if form.active_status.data == LabelTaskActiveStatusEnum.ACTIVATED.value:
        task_status = LabelTaskStatusEnum.ONGONING.value

    with db_v2.auto_commit():
        if label_task:
            label_task.task_status = task_status
    return EditSuccess(msg=u'任务激活操作成功')


@api.route('/modify-done', methods=['POST'])
@auth.login_required
def lbtask_modify_done():
    id = IDForm().validate_for_api().id.data
    tag_task = LabelTask.query.filter_by(id=id).first_or_404()

    with db_v2.auto_commit():
        tag_task.task_status = LabelTaskStatusEnum.FINISHED.value
        tag_task.finish_time = current_timestamp_sec()

    return ResultSuccess(msg=u'修改语句完成')


LabelTaskViewListItemFields = (
    'create_time', 'id', 'task_code', 'task_name', 'proj_id', 'finish_time', 'create_uid', 'tagger_uid', 'task_status')
LabelTaskViewListItem = namedtuple_with_defaults('LabelTaskViewListItem', LabelTaskViewListItemFields,
                                                 default_values=(None,) * len(LabelTaskViewListItemFields))


@api.route('/list', methods=['POST'])
@auth.login_required
def lbtask_list():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    form = LabelTaskSearchForm().validate_for_api()

    # 权限过滤
    cur_user_info = db_v2.session.query(User, Role).filter(
        User.is_deleted == 0,
        User.rid == Role.id,
        User.id == g.user.uid
    ).first()
    if not cur_user_info:
        raise PageResultSuccess(msg=u'任务列表', data={}, page={'page': 1, 'limit': per_page, 'total': 0})

    cur_user_info = {c: getattr(cur_user_info, c, None) for c in cur_user_info._fields}


    q = db_v2.session.query(LabelTask).order_by(LabelTask.create_time.desc()).filter(
        LabelTask.is_deleted == 0)

    if form.create_time_left.data:
        q = q.filter(LabelTask.create_time >= form.create_time_left.data)
    if form.create_time_right.data:
        q = q.filter(LabelTask.create_time <= form.create_time_right.data)
    if form.proj_code.data:
        label_proj_ids = [label_proj.id for label_proj in LabelProject.query.filter(
            LabelProject.proj_code.like('%' + form.proj_code.data + "%")).filter_by().all()]
        q = q.filter(LabelTask.proj_id.in_(label_proj_ids))
    if form.task_code.data:
        q = q.filter(LabelTask.task_code.like('%' + form.task_code.data + "%"))
    if form.task_status.data is not None and form.task_status.data != '':
        q = q.filter(LabelTask.task_status == form.task_status.data)

    # 权限过滤
    if cur_user_info['Role'].rgroup != 0:
        if cur_user_info['Role'].rgroup == 1:
            q = q.filter(
                LabelTask.task_code.like('{}%'.format(current_app.config['BUSI_LBTASK_CODE_PREFIX']))
            )
            if cur_user_info['Role'].rcode == 'taskmanager':
                q = q.filter(LabelTask.create_uid == cur_user_info['User'].id)
            elif cur_user_info['Role'].rcode == 'taskoperator':
                q = q.filter(
                    LabelUserMap.is_deleted == 0,
                    LabelUserMap.rel_type == LabelUserMapRelTypeEnum.TASK.value,
                    LabelUserMap.rel_id == LabelTask.id,
                    LabelUserMap.uid == cur_user_info['User'].id
                )
                q = q.filter(LabelTask.task_status != LabelTaskStatusEnum.INACTIVED.value)
        if cur_user_info['Role'].rgroup == 2:
            q = q.filter(or_(
                LabelTask.task_code.like('{}%'.format(current_app.config['BUSI_LBTASK_SV_CODE_PREFIX'])),
                LabelTask.task_code.like('{}%'.format(current_app.config['BUSI_LBTASK_AUTO_SELECT_CODE_PREFIX']))
            ))

    rvs = pager(q, page=cur_page, per_page=per_page)

    vms = []
    for label_task in rvs.items:
        vm = LabelTaskViewListItem()._asdict()
        vm = dict(zip(vm.keys(), [dict(vm, **label_task)[x] for x in vm.keys()]))

        # TODO 改为对数据库只查一次，数量少则预先用hashmap
        tagger_users = db_v2.session.query(User.id, User.nickname).filter(
            LabelUserMap.is_deleted == 0,
            LabelUserMap.rel_id == label_task.id,
            LabelUserMap.rel_type == LabelUserMapRelTypeEnum.TASK.value,
            LabelUserMap.uid == User.id).filter_by().all()

        vm['taggers'] = [{'uid': uid, 'name': name} for uid, name in tagger_users]

        # TODO 标注数,一次sql获取
        q_cnt = db_v2.session.query(LabelResult, LabelUtteranceInfo).filter(
            LabelResult.request_id == LabelUtteranceInfo.request_id,
            LabelUtteranceInfo.is_deleted == 0,
            LabelResult.task_id == label_task.id).filter_by()

        cnt_all = q_cnt.count()
        q_cnt = q_cnt.filter_by(label_status=1)
        cnt_tagged = q_cnt.count()
        # cnt_all, cnt_tagged = (0, 0)
        vm['cnt_tagged'] = cnt_tagged  # 已标注数
        vm['cnt_all'] = cnt_all  # 任务标注总数
        cumulative_rate = 0
        if label_task.task_status != 0 and cnt_all > 0:
            cumulative_rate = math.floor(float(cnt_tagged) / cnt_all * 100)
        vm['cumulative_rate'] = cumulative_rate  # 任务进度

        vms.append(vm)

    # 创建用户
    create_uids = list(set([vm['create_uid'] for vm in vms]))
    user_list = db_v2.session.query(User).filter(
        User.is_deleted == 0,
        User.id.in_(create_uids)).all()
    user_dict = {user.id: user for user in user_list}
    vm_keys_user = ['nickname', ]
    vm_keys_user_default = {
        'nickname': '系统'
    }
    for vm in vms:
        for v_key in vm_keys_user:
            if user_dict.get(vm['create_uid']):
                vm['creator_{}'.format(v_key)] = getattr(user_dict[vm['create_uid']], v_key, None)
            else:
                vm['creator_{}'.format(v_key)] = vm_keys_user_default.get(v_key, None)

    # 项目信息补全
    label_proj_ids = list(set([vm['proj_id'] for vm in vms]))
    label_proj_list = db_v2.session.query(LabelProject).filter(
        LabelProject.is_deleted == 0,
        LabelProject.id.in_(label_proj_ids)).all()
    label_proj_dict = {label_proj.id: label_proj for label_proj in label_proj_list}
    vm_keys_label_proj = ['proj_name', 'proj_code']
    for vm in vms:
        for v_key in vm_keys_label_proj:
            if label_proj_dict.get(vm['proj_id']):
                vm[v_key] = getattr(label_proj_dict[vm['proj_id']], v_key, None)

    return PageResultSuccess(msg=u'任务列表', data=vms, page=rvs.page_view())


@api.route('/list-uttrs', methods=['POST'])
@auth.login_required
def lbtask_list_utterance():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    form = UtteranceSearchForm().validate_for_api()

    q = db_v2.session.query(LabelResult, LabelUtteranceInfo).filter(
        LabelResult.request_id == LabelUtteranceInfo.request_id).filter_by(
        task_id=IDForm().validate_for_api().id.data).order_by(desc(LabelUtteranceInfo.time),
                                                              LabelUtteranceInfo.id)

    if form.label_status.data is not None and form.label_status.data != '':
        q = q.filter(LabelResult.label_status == form.label_status.data)
    if form.stt_time_left.data and form.stt_time_right.data != '':
        q = q.filter(LabelUtteranceInfo.time >= datetime.fromtimestamp(form.stt_time_left.data))
    if form.stt_time_right.data and form.stt_time_right.data != '':
        q = q.filter(LabelUtteranceInfo.time <= datetime.fromtimestamp(form.stt_time_right.data))

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
    rvs = pager(q_final, page=cur_page, per_page=per_page)

    vms = []
    for rv in rvs.items:
        rv_dict = {c: getattr(rv, c, None) for c in rv._fields}
        vm = {}

        vm['request_id'] = rv_dict['{}_{}'.format(LabelUtteranceInfo.__tablename__, 'request_id')]
        vm['stt_time'] = datetime2timestamp(rv_dict['{}_{}'.format(LabelUtteranceInfo.__tablename__, 'time')])
        vm['lexical_no_symbol'] = rv_dict['{}_{}'.format(LabelUtteranceInfo.__tablename__, 'result')]
        vm['label_status'] = rv_dict['{}_{}'.format(LabelResult.__tablename__, 'label_status')]
        vm['label_text'] = rv_dict['{}_{}'.format(LabelResult.__tablename__, 'label_text')]
        vm['wer'] = rv_dict['{}_{}'.format(LabelResult.__tablename__, 'wer')]
        vms.append(vm)

    return PageResultSuccess(msg=u'任务关联语句列表', data=vms, page=rvs.page_view())


@api.route('/info-uttrs', methods=['POST'])
@auth.login_required
def lbtask_info_utterance():
    # TODO
    id = IDForm().validate_for_api().id.data

    CreateUser = aliased(User)
    TaggerUser = aliased(User)
    label_task, label_project, create_user, tagger_user = db_v2.session.query(LabelTask, LabelProject, CreateUser,
                                                                              TaggerUser).filter(
        LabelTask.tagger_uid == TaggerUser.id,
        LabelTask.create_uid == CreateUser.id,
        LabelTask.proj_id == LabelProject.id).filter_by(id=id).first_or_404()

    vm = LabelTaskViewListItem()._asdict()
    vm = dict(zip(vm.keys(), [dict(vm, **label_task)[x] for x in vm.keys()]))
    vm['proj_code'] = label_project.proj_code
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


@api.route('/set-all-uttrs', methods=['POST'])
@auth.login_required
def lbtask_set_all_utterance():
    task_id = LabelTaskIDForm().validate_for_api().task_id.data
    label_task = LabelTask.query.filter_by(id=task_id).first_or_404()
    form = UtteranceRefSearchForm().validate_for_api()

    # 修改label_result 和 web库的uttr_status
    q = db_v2.session.query(LabelResult, LabelUtteranceInfo).filter(
        LabelResult.is_deleted == 0,
        LabelUtteranceInfo.is_deleted == 0,
        # LabelUtteranceInfo.uttr_status == UtteranceStatusEnum.ASSIGNED_PROJ.value,      # TODO
        LabelUtteranceInfo.request_id == LabelResult.request_id,
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
    rvs = q.all()

    req_id_list = [uttr_info.request_id for _, uttr_info in rvs]
    # 修改engine库的uttr_status
    uttr_audio_list = []
    select_in_step = current_app.config['SQLALCHEMY_CUSTOM_SELECT_IN_STEP']  # TODO 封装
    select_in_from = 0
    select_in_to = select_in_from + select_in_step
    select_in_loop_counter = 0
    select_in_loop_counter_limit = int(len(req_id_list) / select_in_step) + 2
    while True:
        if len(req_id_list[select_in_from:select_in_to]) < 1 or select_in_loop_counter > select_in_loop_counter_limit:
            logger.debug('counter: {}'.format(select_in_loop_counter))
            break

        rvs_part = UtteranceAudio.query.filter(
            # UtteranceAudio.uttr_status == UtteranceStatusEnum.ASSIGNED_PROJ.value,      # TODO
            UtteranceAudio.request_id.in_(req_id_list[select_in_from:select_in_to])).filter_by().all()
        uttr_audio_list += rvs_part

        select_in_from = select_in_to
        select_in_to = select_in_from + select_in_step
        select_in_loop_counter += 1
    logger.debug('length of {}: {}'.format('uttr_audio_list', len(uttr_audio_list)))

    with db_v2.auto_commit():
        for uttr_audio in uttr_audio_list:
            uttr_audio.uttr_status = UtteranceStatusEnum.ASSIGNED_TASK.value
        for label_result, uttr_info in rvs:
            label_result.task_id = label_task.id
            label_result.task_name = label_task.task_name
            label_result.task_code = label_task.task_code

            uttr_info.uttr_status = UtteranceStatusEnum.ASSIGNED_TASK.value

    return Success(msg=u'任务语句关联成功')


@api.route('/set-uttrs', methods=['POST'])
@auth.login_required
def lbtask_set_utterance():
    form = LabelTaskUtteranceMapForm().validate_for_api()

    req_id_list = form.req_id_list.data

    label_task = LabelTask.query.filter_by(id=form.task_id.data).first_or_404()

    # 修改结果表
    label_result_list = []
    select_in_step = current_app.config['SQLALCHEMY_CUSTOM_SELECT_IN_STEP']  # TODO 封装
    select_in_from = 0
    select_in_to = select_in_from + select_in_step
    select_in_loop_counter = 0
    select_in_loop_counter_limit = int(len(req_id_list) / select_in_step) + 2
    while True:
        if len(req_id_list[select_in_from:select_in_to]) < 1 or select_in_loop_counter > select_in_loop_counter_limit:
            logger.debug('counter: {}'.format(select_in_loop_counter))
            break

        rvs_part = LabelResult.query.filter(
            LabelResult.proj_id == label_task.proj_id,
            LabelResult.request_id.in_(req_id_list[select_in_from:select_in_to])).filter_by().all()
        label_result_list += rvs_part

        select_in_from = select_in_to
        select_in_to = select_in_from + select_in_step
        select_in_loop_counter += 1
    logger.debug('length of {}: {}'.format('label_result_list', len(label_result_list)))

    # 修改uttr_info的uttr_status
    uttr_info_list = []
    select_in_step = current_app.config['SQLALCHEMY_CUSTOM_SELECT_IN_STEP']  # TODO 封装
    select_in_from = 0
    select_in_to = select_in_from + select_in_step
    select_in_loop_counter = 0
    select_in_loop_counter_limit = int(len(req_id_list) / select_in_step) + 2
    while True:
        if len(req_id_list[select_in_from:select_in_to]) < 1 or select_in_loop_counter > select_in_loop_counter_limit:
            logger.debug('counter: {}'.format(select_in_loop_counter))
            break

        rvs_part = LabelUtteranceInfo.query.filter(
            # LabelUtteranceInfo.uttr_status == UtteranceStatusEnum.ASSIGNED_PROJ.value,      # TODO
            LabelUtteranceInfo.request_id.in_(req_id_list[select_in_from:select_in_to])).filter_by().all()
        uttr_info_list += rvs_part

        select_in_from = select_in_to
        select_in_to = select_in_from + select_in_step
        select_in_loop_counter += 1
    logger.debug('length of {}: {}'.format('uttr_info_list', len(uttr_info_list)))

    # 修改engine库的uttr_status
    uttr_audio_list = []
    select_in_step = current_app.config['SQLALCHEMY_CUSTOM_SELECT_IN_STEP']  # TODO 封装
    select_in_from = 0
    select_in_to = select_in_from + select_in_step
    select_in_loop_counter = 0
    select_in_loop_counter_limit = int(len(req_id_list) / select_in_step) + 2
    while True:
        if len(req_id_list[select_in_from:select_in_to]) < 1 or select_in_loop_counter > select_in_loop_counter_limit:
            logger.debug('counter: {}'.format(select_in_loop_counter))
            break

        rvs_part = UtteranceAudio.query.filter(
            # UtteranceAudio.uttr_status == UtteranceStatusEnum.ASSIGNED_PROJ.value,      # TODO
            UtteranceAudio.request_id.in_(req_id_list[select_in_from:select_in_to])).filter_by().all()
        uttr_audio_list += rvs_part

        select_in_from = select_in_to
        select_in_to = select_in_from + select_in_step
        select_in_loop_counter += 1
    logger.debug('length of {}: {}'.format('uttr_audio_list', len(uttr_audio_list)))

    #
    with db_v2.auto_commit():
        for uttr_info in uttr_info_list:
            uttr_info.uttr_status = UtteranceStatusEnum.ASSIGNED_TASK.value
        for uttr_audio in uttr_audio_list:
            uttr_audio.uttr_status = UtteranceStatusEnum.ASSIGNED_TASK.value
        for label_result in label_result_list:
            label_result.task_id = label_task.id
            label_result.task_name = label_task.task_name
            label_result.task_code = label_task.task_code

    return Success(msg=u'任务语句关联成功')


@api.route('/set-all-sv-uttrs', methods=['POST'])
@auth.login_required
def lbtask_set_all_supervisor_utterance():
    # TODO
    task_form = LabelTaskAddSVForm().validate_for_api()
    req_id_list = UtteranceIDListForm().validate_for_api().req_id_list.data

    column_name, column_order = ColumnSortForm.fetch_column_param(ColumnSortForm().validate_for_api())
    form = UtteranceSVSearchForm().validate_for_api()

    # 任務处理
    label_task = LabelTask.query.filter_by(id=task_form.task_id.data).first()
    if not label_task:
        # 新建任务
        label_task = LabelTask()
        task_code_prefix = current_app.config['BUSI_LBTASK_SV_CODE_PREFIX']
        placeholder_num = current_app.config['BUSI_LBTASK_SV_CODE_PLACEHOLDER_NUM']
        task_code_list = LabelTask.query.with_entities(LabelTask.task_code).filter(
            LabelTask.task_code.like(task_code_prefix + '%')).filter_by(
            with_deleted=True).all()
        task_cnt_by_code = max(
            [int(task_code[-min(placeholder_num, len(task_code) - len(task_code_prefix)):]) for task_code, in
             task_code_list]) if len(
            task_code_list) > 0 else 0
        task_code = task_code_prefix + str(task_cnt_by_code + 1).zfill(placeholder_num)

        label_task.task_code = task_code
        label_task.task_name = task_form.task_name.data
        label_task.create_time = current_timestamp_sec()
        label_task.create_uid = g.user.uid
        label_task.task_status = LabelTaskStatusEnum.ONGONING.value
        label_task.proj_id = -1

        with db_v2.auto_commit():
            db_v2.session.add(label_task)

        # 添加标注人员
        label_task_user_map = LabelUserMap()
        label_task_user_map.rel_id = label_task.id
        label_task_user_map.rel_type = LabelUserMapRelTypeEnum.TASK.value
        label_task_user_map.uid = g.user.uid

        with db_v2.auto_commit():
            db_v2.session.add(label_task_user_map)

    # 迁入web库
    rvs_uttr = []
    if True:
        select_in_step = current_app.config['SQLALCHEMY_CUSTOM_SELECT_IN_STEP']  # TODO 封装
        select_in_from = 0
        select_in_to = select_in_from + select_in_step
        select_in_loop_counter = 0
        select_in_loop_counter_limit = int(len(req_id_list) / select_in_step) + 2
        while True:
            if len(req_id_list[
                   select_in_from:select_in_to]) < 1 or select_in_loop_counter > select_in_loop_counter_limit:
                logger.info('counter: {}'.format(select_in_loop_counter))
                break
            rvs_uttr_part = db_v2.session.query(UtteranceAudio, UtteranceAccess).filter(
                UtteranceAudio.is_deleted == 0,
                UtteranceAccess.is_deleted == 0,
                UtteranceAudio.request_id == UtteranceAccess.request_id,
                UtteranceAudio.request_id.in_(req_id_list[select_in_from:select_in_to]),
                UtteranceAudio.uttr_status == UtteranceStatusEnum.PARSED.value).all()
            rvs_uttr += rvs_uttr_part

            select_in_from = select_in_to
            select_in_to = select_in_from + select_in_step
            select_in_loop_counter += 1
        logger.info('length of {}: {}'.format('rvs_uttr', len(rvs_uttr)))

    rvs_diting = []
    if True:
        select_in_step = current_app.config['SQLALCHEMY_CUSTOM_SELECT_IN_STEP']  # TODO 封装
        select_in_from = 0
        select_in_to = select_in_from + select_in_step
        select_in_loop_counter = 0
        select_in_loop_counter_limit = int(len(req_id_list) / select_in_step) + 2
        while True:
            if len(req_id_list[
                   select_in_from:select_in_to]) < 1 or select_in_loop_counter > select_in_loop_counter_limit:
                logger.info('counter: {}'.format(select_in_loop_counter))
                break
            rvs_diting_part = db_v2.session.query(NgDiting, NgDitingRelation).filter(
                NgDiting.is_deleted == 0,
                NgDitingRelation.is_deleted == 0,
                NgDiting.uuid == NgDitingRelation.uuid,
                UtteranceAudio.request_id.in_(req_id_list[select_in_from:select_in_to]),
                UtteranceAudio.request_id == NgDiting.request_id,
                UtteranceAudio.uttr_status == UtteranceStatusEnum.PARSED.value).all()
            rvs_diting += rvs_diting_part

            select_in_from = select_in_to
            select_in_to = select_in_from + select_in_step
            select_in_loop_counter += 1
        logger.info('length of {}: {}'.format('rvs_diting', len(rvs_diting)))

    utterance_info_list = []
    utterance_audio_list = []
    if True:
        for uttr_audio, uttr_access in rvs_uttr:
            utterance_info = LabelUtteranceInfo()
            for v_key in uttr_audio.keys():
                if v_key in ['id', 'insert_time', 'is_deleted', ]:
                    continue
                setattr(utterance_info, v_key, getattr(uttr_audio, v_key, None))
            for v_key in uttr_access.keys():
                if v_key in ['id', 'insert_time', 'is_deleted', ]:
                    continue
                setattr(utterance_info, v_key, getattr(uttr_access, v_key, None))
            utterance_info.uttr_status = UtteranceStatusEnum.SELECTED.value
            utterance_audio_list.append(uttr_audio)
            utterance_info_list.append(utterance_info)

    diting_info_list = []
    if True:
        for diting, diting_relation in rvs_diting:
            diting_info = LabelDitingInfo()
            for v_key in diting.keys():
                if v_key in ['id', 'insert_time', 'is_deleted', ]:
                    continue
                setattr(diting_info, v_key, getattr(diting, v_key, None))
            for v_key in diting_relation.keys():
                if v_key in ['id', 'insert_time', 'is_deleted', ]:
                    continue
                setattr(diting_info, v_key, getattr(diting_relation, v_key, None))
            diting_info_list.append(diting_info)

    with db_v2.auto_commit():
        for utterance_audio in utterance_audio_list:
            utterance_audio.uttr_status = UtteranceStatusEnum.SELECTED.value
        # db_v2.session.bulk_save_objects(utterance_info_list)
        utterance_info_dict_list = [dict(utterance_info) for utterance_info in utterance_info_list]
        db_v2.session.execute(LabelUtteranceInfo.__table__.insert().prefix_with('IGNORE'), utterance_info_dict_list)
        # db_v2.session.bulk_save_objects(diting_info_list)
        diting_info_dict_list = [dict(diting_info) for diting_info in diting_info_list]
        db_v2.session.execute(LabelDitingInfo.__table__.insert().prefix_with('IGNORE'), diting_info_dict_list)

    # 任务与语句关联
    uttr_info_list = []
    if True:
        select_in_step = current_app.config['SQLALCHEMY_CUSTOM_SELECT_IN_STEP']  # TODO 封装
        select_in_from = 0
        select_in_to = select_in_from + select_in_step
        select_in_loop_counter = 0
        select_in_loop_counter_limit = int(len(req_id_list) / select_in_step) + 2
        while True:
            if len(req_id_list[
                   select_in_from:select_in_to]) < 1 or select_in_loop_counter > select_in_loop_counter_limit:
                logger.info('counter: {}'.format(select_in_loop_counter))
                break
            rvs_part = db_v2.session.query(LabelUtteranceInfo).filter(
                LabelUtteranceInfo.is_deleted == 0,
                LabelUtteranceInfo.request_id.in_(req_id_list[select_in_from:select_in_to])).all()
            uttr_info_list += rvs_part

            select_in_from = select_in_to
            select_in_to = select_in_from + select_in_step
            select_in_loop_counter += 1
        logger.info('length of {}: {}'.format('uttr_info_list', len(uttr_info_list)))

    uttr_audio_list = []
    if True:
        select_in_step = current_app.config['SQLALCHEMY_CUSTOM_SELECT_IN_STEP']  # TODO 封装
        select_in_from = 0
        select_in_to = select_in_from + select_in_step
        select_in_loop_counter = 0
        select_in_loop_counter_limit = int(len(req_id_list) / select_in_step) + 2
        while True:
            if len(req_id_list[
                   select_in_from:select_in_to]) < 1 or select_in_loop_counter > select_in_loop_counter_limit:
                logger.info('counter: {}'.format(select_in_loop_counter))
                break
            rvs_part = db_v2.session.query(UtteranceAudio).filter(
                UtteranceAudio.is_deleted == 0,
                UtteranceAudio.request_id.in_(req_id_list[select_in_from:select_in_to])).all()
            uttr_audio_list += rvs_part

            select_in_from = select_in_to
            select_in_to = select_in_from + select_in_step
            select_in_loop_counter += 1
        logger.info('length of {}: {}'.format('uttr_audio_list', len(uttr_audio_list)))

    current_t = current_timestamp_sec()
    label_result_list = []
    if True:
        for uttr_info in uttr_info_list:
            label_result = LabelResult()
            label_result.request_id = uttr_info.request_id
            label_result.uttr_url = uttr_info.url
            label_result.uttr_result = uttr_info.result
            label_result.uttr_stt_time = datetime2timestamp(uttr_info.time)
            label_result.proj_id = -1
            label_result.task_id = label_task.id
            label_result.task_code = label_task.task_code
            label_result.task_name = label_task.task_name
            label_result.create_time = current_t
            label_result_list.append(label_result)

    with db_v2.auto_commit():
        db_v2.session.bulk_save_objects(label_result_list)
        for uttr_info in uttr_info_list:
            uttr_info.uttr_status = UtteranceStatusEnum.ASSIGNED_TASK.value
        for uttr_audio in uttr_audio_list:
            uttr_audio.uttr_status = UtteranceStatusEnum.ASSIGNED_TASK.value

    return Success(msg=u'运维任务设置成功')


@api.route('/set-sv-uttrs', methods=['POST'])
@auth.login_required
def lbtask_set_supervisor_utterance():
    task_form = LabelTaskAddSVForm().validate_for_api()
    req_id_list = UtteranceIDListForm().validate_for_api().req_id_list.data

    # 排除已分配了任务的req_id
    req_id_set = set(req_id_list)
    exclude_req_ids = []
    select_in_step = current_app.config['SQLALCHEMY_CUSTOM_SELECT_IN_STEP']  # TODO 封装
    select_in_from = 0
    select_in_to = select_in_from + select_in_step
    select_in_loop_counter = 0
    select_in_loop_counter_limit = int(len(req_id_list) / select_in_step) + 2
    while True:
        if len(req_id_list[
               select_in_from:select_in_to]) < 1 or select_in_loop_counter > select_in_loop_counter_limit:
            logger.info('counter: {}'.format(select_in_loop_counter))
            break
        exclude_req_ids_part = db_v2.session.query(LabelResult.request_id).filter(
            LabelResult.is_deleted == 0,
            LabelResult.task_id != -1,
            LabelResult.request_id.in_(req_id_list[select_in_from:select_in_to]),
        ).all()
        exclude_req_ids += exclude_req_ids_part

        select_in_from = select_in_to
        select_in_to = select_in_from + select_in_step
        select_in_loop_counter += 1
    logger.info('length of {}: {}'.format('exclude_req_ids', len(exclude_req_ids)))
    exclude_req_ids = [req_id for req_id, in exclude_req_ids]
    req_id_list_diff = list(req_id_set.difference(set(exclude_req_ids)))

    if len(req_id_list) < 1:
        raise ParameterException(msg=u'语句没有选中')
    if len(req_id_list_diff) < 1:
        raise ParameterException(msg=u'选中语句已被全部分配')
    req_id_list = req_id_list_diff

    # 任務处理
    label_task = LabelTask.query.filter_by(id=task_form.task_id.data).first()
    if not label_task:
        # 新建任务
        label_task = LabelTask()
        task_code_prefix = current_app.config['BUSI_LBTASK_SV_CODE_PREFIX']
        placeholder_num = current_app.config['BUSI_LBTASK_SV_CODE_PLACEHOLDER_NUM']
        task_code_list = LabelTask.query.with_entities(LabelTask.task_code).filter(
            LabelTask.task_code.like(task_code_prefix + '%')).filter_by(
            with_deleted=True).all()
        task_cnt_by_code = max(
            [int(task_code[-min(placeholder_num, len(task_code) - len(task_code_prefix)):]) for task_code, in
             task_code_list]) if len(
            task_code_list) > 0 else 0
        task_code = task_code_prefix + str(task_cnt_by_code + 1).zfill(placeholder_num)

        label_task.task_code = task_code
        label_task.task_name = task_form.task_name.data
        label_task.create_time = current_timestamp_sec()
        label_task.create_uid = g.user.uid
        label_task.task_status = LabelTaskStatusEnum.ONGONING.value
        label_task.proj_id = -1

        with db_v2.auto_commit():
            db_v2.session.add(label_task)

        # 添加标注人员
        label_task_user_map = LabelUserMap()
        label_task_user_map.rel_id = label_task.id
        label_task_user_map.rel_type = LabelUserMapRelTypeEnum.TASK.value
        label_task_user_map.uid = g.user.uid

        with db_v2.auto_commit():
            db_v2.session.add(label_task_user_map)

    # 迁入web库
    rvs_uttr = []
    if True:
        select_in_step = current_app.config['SQLALCHEMY_CUSTOM_SELECT_IN_STEP']  # TODO 封装
        select_in_from = 0
        select_in_to = select_in_from + select_in_step
        select_in_loop_counter = 0
        select_in_loop_counter_limit = int(len(req_id_list) / select_in_step) + 2
        while True:
            if len(req_id_list[
                   select_in_from:select_in_to]) < 1 or select_in_loop_counter > select_in_loop_counter_limit:
                logger.info('counter: {}'.format(select_in_loop_counter))
                break
            rvs_uttr_part = db_v2.session.query(UtteranceAudio, UtteranceAccess).filter(
                UtteranceAudio.is_deleted == 0,
                UtteranceAccess.is_deleted == 0,
                UtteranceAudio.request_id == UtteranceAccess.request_id,
                UtteranceAudio.request_id.in_(req_id_list[select_in_from:select_in_to]),
                UtteranceAudio.uttr_status == UtteranceStatusEnum.PARSED.value).all()
            rvs_uttr += rvs_uttr_part

            select_in_from = select_in_to
            select_in_to = select_in_from + select_in_step
            select_in_loop_counter += 1
        logger.info('length of {}: {}'.format('rvs_uttr', len(rvs_uttr)))

    rvs_diting = []
    if True:
        select_in_step = current_app.config['SQLALCHEMY_CUSTOM_SELECT_IN_STEP']  # TODO 封装
        select_in_from = 0
        select_in_to = select_in_from + select_in_step
        select_in_loop_counter = 0
        select_in_loop_counter_limit = int(len(req_id_list) / select_in_step) + 2
        while True:
            if len(req_id_list[
                   select_in_from:select_in_to]) < 1 or select_in_loop_counter > select_in_loop_counter_limit:
                logger.info('counter: {}'.format(select_in_loop_counter))
                break
            rvs_diting_part = db_v2.session.query(NgDiting, NgDitingRelation).filter(
                NgDiting.is_deleted == 0,
                NgDitingRelation.is_deleted == 0,
                NgDiting.uuid == NgDitingRelation.uuid,
                UtteranceAudio.request_id.in_(req_id_list[select_in_from:select_in_to]),
                UtteranceAudio.request_id == NgDiting.request_id,
                UtteranceAudio.uttr_status == UtteranceStatusEnum.PARSED.value).all()
            rvs_diting += rvs_diting_part

            select_in_from = select_in_to
            select_in_to = select_in_from + select_in_step
            select_in_loop_counter += 1
        logger.info('length of {}: {}'.format('rvs_diting', len(rvs_diting)))

    utterance_info_list = []
    utterance_audio_list = []
    if True:
        for uttr_audio, uttr_access in rvs_uttr:
            utterance_info = LabelUtteranceInfo()
            for v_key in uttr_audio.keys():
                if v_key in ['id', 'insert_time', 'is_deleted', ]:
                    continue
                setattr(utterance_info, v_key, getattr(uttr_audio, v_key, None))
            for v_key in uttr_access.keys():
                if v_key in ['id', 'insert_time', 'is_deleted', ]:
                    continue
                setattr(utterance_info, v_key, getattr(uttr_access, v_key, None))
            utterance_info.uttr_status = UtteranceStatusEnum.SELECTED.value
            utterance_info_list.append(utterance_info)

            utterance_audio_list.append(uttr_audio)

    diting_info_list = []
    if True:
        for diting, diting_relation in rvs_diting:
            diting_info = LabelDitingInfo()
            for v_key in diting.keys():
                if v_key in ['id', 'insert_time', 'is_deleted', ]:
                    continue
                setattr(diting_info, v_key, getattr(diting, v_key, None))
            for v_key in diting_relation.keys():
                if v_key in ['id', 'insert_time', 'is_deleted', ]:
                    continue
                setattr(diting_info, v_key, getattr(diting_relation, v_key, None))
            diting_info_list.append(diting_info)

    with db_v2.auto_commit():
        for utterance_audio in utterance_audio_list:
            utterance_audio.uttr_status = UtteranceStatusEnum.SELECTED.value
        # db_v2.session.bulk_save_objects(utterance_info_list)
        utterance_info_dict_list = [dict(utterance_info) for utterance_info in utterance_info_list]
        db_v2.session.execute(LabelUtteranceInfo.__table__.insert().prefix_with('IGNORE'), utterance_info_dict_list)
        # db_v2.session.bulk_save_objects(diting_info_list)
        diting_info_dict_list = [dict(diting_info) for diting_info in diting_info_list]
        db_v2.session.execute(LabelDitingInfo.__table__.insert().prefix_with('IGNORE'), diting_info_dict_list)

    # 任务与语句关联
    uttr_info_list = []
    if True:
        select_in_step = current_app.config['SQLALCHEMY_CUSTOM_SELECT_IN_STEP']  # TODO 封装
        select_in_from = 0
        select_in_to = select_in_from + select_in_step
        select_in_loop_counter = 0
        select_in_loop_counter_limit = int(len(req_id_list) / select_in_step) + 2
        while True:
            if len(req_id_list[
                   select_in_from:select_in_to]) < 1 or select_in_loop_counter > select_in_loop_counter_limit:
                logger.info('counter: {}'.format(select_in_loop_counter))
                break
            rvs_part = db_v2.session.query(LabelUtteranceInfo).filter(
                LabelUtteranceInfo.is_deleted == 0,
                LabelUtteranceInfo.request_id.in_(req_id_list[select_in_from:select_in_to])).all()
            uttr_info_list += rvs_part

            select_in_from = select_in_to
            select_in_to = select_in_from + select_in_step
            select_in_loop_counter += 1
        logger.info('length of {}: {}'.format('uttr_info_list', len(uttr_info_list)))

    uttr_audio_list = []
    if True:
        select_in_step = current_app.config['SQLALCHEMY_CUSTOM_SELECT_IN_STEP']  # TODO 封装
        select_in_from = 0
        select_in_to = select_in_from + select_in_step
        select_in_loop_counter = 0
        select_in_loop_counter_limit = int(len(req_id_list) / select_in_step) + 2
        while True:
            if len(req_id_list[
                   select_in_from:select_in_to]) < 1 or select_in_loop_counter > select_in_loop_counter_limit:
                logger.info('counter: {}'.format(select_in_loop_counter))
                break
            rvs_part = db_v2.session.query(UtteranceAudio).filter(
                UtteranceAudio.is_deleted == 0,
                UtteranceAudio.request_id.in_(req_id_list[select_in_from:select_in_to])).all()
            uttr_audio_list += rvs_part

            select_in_from = select_in_to
            select_in_to = select_in_from + select_in_step
            select_in_loop_counter += 1
        logger.info('length of {}: {}'.format('uttr_audio_list', len(uttr_audio_list)))

    current_t = current_timestamp_sec()
    label_result_list = []
    if True:
        for uttr_info in uttr_info_list:
            label_result = LabelResult()
            label_result.request_id = uttr_info.request_id
            label_result.uttr_url = uttr_info.url
            label_result.uttr_result = uttr_info.result
            label_result.uttr_stt_time = datetime2timestamp(uttr_info.time)
            label_result.proj_id = -1
            label_result.task_id = label_task.id
            label_result.task_code = label_task.task_code
            label_result.task_name = label_task.task_name
            label_result.create_time = current_t
            label_result_list.append(label_result)

    with db_v2.auto_commit():
        db_v2.session.bulk_save_objects(label_result_list)
        for uttr_info in uttr_info_list:
            uttr_info.uttr_status = UtteranceStatusEnum.ASSIGNED_TASK.value
        for uttr_audio in uttr_audio_list:
            uttr_audio.uttr_status = UtteranceStatusEnum.ASSIGNED_TASK.value

    return Success(msg=u'运维任务设置成功')


@api.route('/del-uttrs', methods=['POST'])
@auth.login_required
def lbtask_del_utterance():
    form = LabelTaskUtteranceMapForm().validate_for_api()
    req_id_list = form.req_id_list.data

    if not req_id_list or len(req_id_list) < 1:
        raise ParameterException(msg=u'未选中任何语句')

    rvs = []
    if True:
        select_in_step = current_app.config['SQLALCHEMY_CUSTOM_SELECT_IN_STEP']  # TODO 封装
        select_in_from = 0
        select_in_to = select_in_from + select_in_step
        select_in_loop_counter = 0
        select_in_loop_counter_limit = int(len(req_id_list) / select_in_step) + 2
        while True:
            if len(req_id_list[
                   select_in_from:select_in_to]) < 1 or select_in_loop_counter > select_in_loop_counter_limit:
                logger.debug('counter: {}'.format(select_in_loop_counter))
                break

            rvs_part = db_v2.session.query(LabelResult, LabelUtteranceInfo).filter(
                LabelResult.task_id == form.task_id.data,
                LabelResult.request_id == LabelUtteranceInfo.request_id,
                LabelUtteranceInfo.request_id.in_(req_id_list[select_in_from:select_in_to])).all()
            rvs += rvs_part

            select_in_from = select_in_to
            select_in_to = select_in_from + select_in_step
            select_in_loop_counter += 1
        logger.debug('rvs length: {}'.format(len(rvs)))

    # 同步engine库
    uttr_audio_list = []
    select_in_step = current_app.config['SQLALCHEMY_CUSTOM_SELECT_IN_STEP']  # TODO 封装
    select_in_from = 0
    select_in_to = select_in_from + select_in_step
    select_in_loop_counter = 0
    select_in_loop_counter_limit = int(len(req_id_list) / select_in_step) + 2
    while True:
        if len(req_id_list[
               select_in_from:select_in_to]) < 1 or select_in_loop_counter > select_in_loop_counter_limit:
            logger.debug('counter: {}'.format(select_in_loop_counter))
            break

        rvs_part = db_v2.session.query(UtteranceAudio).filter(
            LabelUtteranceInfo.request_id.in_(req_id_list[select_in_from:select_in_to])).all()
        uttr_audio_list += rvs_part

        select_in_from = select_in_to
        select_in_to = select_in_from + select_in_step
        select_in_loop_counter += 1
    logger.debug('{} length: {}'.format('uttr_audio_list', len(uttr_audio_list)))

    uttr_audio_dict = {uttr_audio.request_id: uttr_audio for uttr_audio in uttr_audio_list}

    with db_v2.auto_commit():
        for label_result, uttr_info in rvs:
            if uttr_info.uttr_status != UtteranceStatusEnum.LABELED.value:
                if label_result.proj_id == -1:
                    uttr_info.uttr_status = UtteranceStatusEnum.SELECTED.value
                else:
                    uttr_info.uttr_status = UtteranceStatusEnum.ASSIGNED_PROJ.value
                uttr_audio = uttr_audio_dict.get(uttr_info.request_id)
                if uttr_audio:
                    uttr_audio.uttr_status = uttr_info.uttr_status

            if label_result.label_status == LabelResultStatusEnum.MARKED.value:
                label_result.is_deleted = 1
            else:
                label_result.task_id = -1
                label_result.task_code = None
                label_result.task_name = None

    return DeleteSuccess(msg=u'任务语句解联成功')


@api.route('/del-all-uttrs', methods=['POST'])
@auth.login_required
def lbtask_del_all_utterance():
    task_id = LabelTaskIDForm().validate_for_api().task_id.data
    form = UtteranceSearchForm().validate_for_api()

    rvs = []
    if True:
        q = db_v2.session.query(LabelResult, LabelUtteranceInfo).filter(
            LabelResult.is_deleted == 0,
            LabelUtteranceInfo.is_deleted == 0,
            LabelUtteranceInfo.request_id == LabelResult.request_id,
            LabelResult.task_id == task_id)

        if form.label_status.data is not None and form.label_status.data != '':
            q = q.filter(LabelResult.label_status == form.label_status.data)
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
        rvs = q.all()

    # 同步engine库
    req_id_list = [uttr_info.request_id for _, uttr_info in rvs]
    uttr_audio_list = []
    select_in_step = current_app.config['SQLALCHEMY_CUSTOM_SELECT_IN_STEP']  # TODO 封装
    select_in_from = 0
    select_in_to = select_in_from + select_in_step
    select_in_loop_counter = 0
    select_in_loop_counter_limit = int(len(req_id_list) / select_in_step) + 2
    while True:
        if len(req_id_list[select_in_from:select_in_to]) < 1 or select_in_loop_counter > select_in_loop_counter_limit:
            logger.debug('counter: {}'.format(select_in_loop_counter))
            break

        rvs_part = db_v2.session.query(UtteranceAudio).filter(
            LabelUtteranceInfo.request_id.in_(req_id_list[select_in_from:select_in_to])).all()
        uttr_audio_list += rvs_part

        select_in_from = select_in_to
        select_in_to = select_in_from + select_in_step
        select_in_loop_counter += 1
    logger.debug('{} length: {}'.format('uttr_audio_list', len(uttr_audio_list)))

    uttr_audio_dict = {uttr_audio.request_id: uttr_audio for uttr_audio in uttr_audio_list}

    with db_v2.auto_commit():
        for label_result, uttr_info in rvs:
            if uttr_info.uttr_status != UtteranceStatusEnum.LABELED.value:
                if label_result.proj_id == -1:
                    uttr_info.uttr_status = UtteranceStatusEnum.SELECTED.value
                else:
                    uttr_info.uttr_status = UtteranceStatusEnum.ASSIGNED_PROJ.value
                uttr_audio = uttr_audio_dict.get(uttr_info.request_id)
                if uttr_audio:
                    uttr_audio.uttr_status = uttr_info.uttr_status

            if label_result.label_status == LabelResultStatusEnum.MARKED.value:
                label_result.is_deleted = 1
            else:
                label_result.task_id = -1
                label_result.task_code = None
                label_result.task_name = None

    return DeleteSuccess(msg=u'任务全部语句解除关联成功')


@api.route('/choices-name', methods=['POST'])
@auth.login_required
def lbtask_choices_name():
    # TODO 权限
    q = db_v2.session.query(LabelTask.id, LabelTask.task_name, LabelTask.task_code).filter_by()
    form = LabelTaskSearchForm().validate_for_api()

    if form.task_code.data:
        q = q.filter(LabelTask.task_code.like('%' + form.task_code.data + "%"))

    rvs = q.all()

    if not rvs:
        return ResultSuccess(msg=u'无任务数据', data=[])

    vms = []
    for id, task_name, task_code in rvs:
        vm = dict(
            k=id,
            v='{}:{}'.format(task_code, task_name)
        )
        vms.append(vm)

    choice_type = int(request.args.get('choice_type', 0) if not request.args.get('choice_type') == 'undefined' else 0)
    if choice_type == ChoicesExTypeEnum.TYPE_NEITHER.value:
        vms.append(dict(k=ChoicesExItemEnum.NEITHER.value, v=u'无参与任务'))
    elif choice_type == ChoicesExTypeEnum.TYPE_ALL.value:
        vms.insert(0, dict(k=ChoicesExItemEnum.ALL.value, v=u'全部任务'))
    elif choice_type == ChoicesExTypeEnum.TYPE_NEITHER_ALL.value:
        vms.insert(0, dict(k=ChoicesExItemEnum.ALL.value, v=u'全部任务'))
        vms.append(dict(k=ChoicesExItemEnum.NEITHER.value, v=u'无参与任务'))

    return ResultSuccess(msg=u'任务名称字典', data=vms)
