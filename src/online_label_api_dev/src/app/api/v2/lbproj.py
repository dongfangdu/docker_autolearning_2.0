# -*- coding: utf-8 -*-
import logging

import time
from datetime import datetime
from flask import g, current_app, request
from operator import or_
from sqlalchemy import desc

from app.libs.builtin_extend import namedtuple_with_defaults, datetime2timestamp, current_timestamp_sec
from app.libs.enums import ChoicesExItemEnum, ChoicesExTypeEnum, UtteranceStatusEnum
from app.libs.error_code import DeleteSuccess, ResultSuccess, CreateSuccess, PageResultSuccess, EditSuccess, Success, \
    ParameterException
from app.libs.qpaginate import pager
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db_v2
from app.models.v2.engine.ng import NgDiting, NgDitingRelation
from app.models.v2.engine.utterance import UtteranceAudio, UtteranceAccess
from app.models.v2.web.common import Region
from app.models.v2.web.label import LabelProject, LabelResult, LabelUtteranceInfo, LabelDitingInfo
from app.models.v2.web.sysmgr import User
from app.validators.base import PageForm
from app.validators.forms_v2 import LabelProjectForm, LabelProjectSearchForm, IDForm, LabelProjectEditForm, \
    LabelProjectUtteranceMapForm, LabelProjectIDForm, UtteranceSearchForm, UtteranceRefSearchForm

api = Redprint('lbproj')
logger = logging.getLogger(__name__)


@api.route('', methods=['POST'])
@auth.login_required
def lbproj_add():
    form = LabelProjectForm().validate_for_api()

    # 生成项目编号
    # region_id = form.region_id.data
    placeholder_num = current_app.config['BUSI_LBPROJECT_CODE_PLACEHOLDER_NUM']
    proj_code_list = LabelProject.query.with_entities(LabelProject.proj_code).filter_by(with_deleted=True).all()
    proj_cnt = max([int(proj_code[-placeholder_num:]) for proj_code, in proj_code_list]) if len(
        proj_code_list) > 0 else 0
    project_code = '{}{}'.format(current_app.config['BUSI_LBPROJECT_CODE_PREFIX'],
                                 str(proj_cnt + 1).zfill(placeholder_num))
    # 生成项目用户
    uid = g.user.uid
    # 区域处理
    region_list = Region.query.filter(Region.id.in_(form.region_ids.data)).order_by(Region.level).all()

    lbproj = LabelProject()
    with db_v2.auto_commit():
        form.populate_obj(lbproj)
        lbproj.proj_code = project_code
        lbproj.create_uid = uid
        lbproj.create_time = int(time.time())
        lbproj.region_id = region_list[-1].id
        lbproj.region_full_ids = ','.join([str(region.id) for region in region_list])
        lbproj.region_full_name = ''.join([region.name for region in region_list])

        db_v2.session.add(lbproj)

    vm = LabelProjectViewListItem()._asdict()
    vm = dict(zip(vm.keys(), [dict(vm, **lbproj)[x] for x in vm.keys()]))
    user = User.query.filter_by(id=lbproj.create_uid).first()
    vm['creator_name'] = user.nickname
    return CreateSuccess(msg=u'项目新增成功', data=vm)


@api.route('/<int:oid>', methods=['GET'])
@auth.login_required
def lbproj_get(oid):
    tagproject = LabelProject.query.filter_by(id=oid).first_or_404()

    vm = LabelProjectViewListItem()._asdict()
    vm = dict(zip(vm.keys(), [dict(vm, **tagproject)[x] for x in vm.keys()]))
    county = Region.query.filter_by(id=tagproject.region_id).first_or_404()
    vm['county_id'] = county.id
    vm['county_name'] = county.name
    city = Region.query.filter_by(id=county.parent_id).first_or_404()
    vm['city_id'] = city.id
    vm['city_name'] = city.name
    province = Region.query.filter_by(id=city.parent_id).first_or_404()
    vm['province_id'] = province.id
    vm['province_name'] = province.name

    return ResultSuccess(msg=u"项目信息", data=vm)


@api.route('/del/<int:oid>', methods=['GET'])
@auth.login_required
def lbproj_del(oid):
    with db_v2.auto_commit():
        label_project = LabelProject.query.filter_by(id=oid).first_or_404()
        label_project.delete()
        # TODO
        # LabelResult.query.filter(LabelResult.proj_id == oid).filter_by().update({'is_deleted': 1})

    return DeleteSuccess(msg=u'项目删除成功')


@api.route('/edit', methods=['POST'])
@auth.login_required
def lbproj_edit():
    id = IDForm().validate_for_api().id.data
    lbproj = LabelProject.query.filter_by(id=id).first_or_404()
    form = LabelProjectEditForm().validate_for_api()

    with db_v2.auto_commit():
        if form.proj_name.data and lbproj.proj_name != form.proj_name.data:
            lbproj.proj_name = form.proj_name.data
            LabelResult.query.filter(LabelResult.proj_id == lbproj.id).update({'proj_name': lbproj.proj_name})
        if form.proj_desc.data and lbproj.proj_desc != form.proj_desc.data:
            lbproj.proj_desc = form.proj_desc.data
        if form.proj_difficulty.data is not None and lbproj.proj_desc != form.proj_difficulty.data:
            lbproj.proj_difficulty = form.proj_difficulty.data
        if form.region_ids.data and len(form.region_ids.data) > 0:
            region_list = Region.query.filter(Region.id.in_(form.region_ids.data)).order_by(Region.level).all()
            lbproj.region_id = region_list[-1].id
            lbproj.region_full_ids = ','.join([str(region.id) for region in region_list])
            lbproj.region_full_name = ''.join([region.name for region in region_list])
    return EditSuccess(msg=u'项目信息修改成功')


LabelProjectViewListItemFields = (
    'id', 'proj_code', 'proj_name', 'proj_desc', 'proj_difficulty', 'create_time', 'region_id', 'region_full_ids',
    'region_full_name')
LabelProjectViewListItem = namedtuple_with_defaults('LabelProjectViewListItem', LabelProjectViewListItemFields,
                                                    default_values=(None,) * len(LabelProjectViewListItemFields))


@api.route('/list', methods=['POST'])
@auth.login_required
def lbproj_list():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    form = LabelProjectSearchForm().validate_for_api()
    q = db_v2.session.query(LabelProject, User).order_by(LabelProject.create_time.desc()).filter(
        LabelProject.create_uid == User.id, LabelProject.is_deleted == 0)
    if form.proj_code.data:
        q = q.filter(LabelProject.proj_code.like('%' + form.proj_code.data + "%"))
    if form.proj_name.data:
        q = q.filter(LabelProject.proj_name.like('%' + form.proj_name.data + "%"))
    if form.region_ids.data and len(form.region_ids.data) > 0:
        region_list = Region.query.filter(Region.id.in_(form.region_ids.data)).order_by(Region.level).all()
        region_full_ids_prefix = ','.join([str(region.id) for region in region_list])
        q = q.filter(LabelProject.region_full_ids.like(region_full_ids_prefix + '%'))
    q = q.filter_by()
    rvs = pager(q, page=cur_page, per_page=per_page)

    vms = []
    for tagproj, user in rvs.items:
        vm = LabelProjectViewListItem()._asdict()
        vm = dict(zip(vm.keys(), [dict(vm, **tagproj)[x] for x in vm.keys()]))
        vm['region_ids'] = [int(region_id) for region_id in vm['region_full_ids'].split(',')]
        vm['creator_name'] = user.nickname
        vms.append(vm)

    return PageResultSuccess(msg=u'标注项目列表', data=vms, page=rvs.page_view())


@api.route('/list-uttrs', methods=['POST'])
@auth.login_required
def lbproj_list_utterance():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    label_project = LabelProject.query.filter_by(id=LabelProjectIDForm().validate_for_api().proj_id.data).first_or_404()
    form = UtteranceSearchForm().validate_for_api()

    q = db_v2.session.query(LabelResult, LabelUtteranceInfo).filter(
        LabelResult.is_deleted == 0,
        LabelResult.proj_id == label_project.id,
        LabelResult.request_id == LabelUtteranceInfo.request_id
    ).order_by(desc(LabelUtteranceInfo.time), LabelUtteranceInfo.id)

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
        vm['detect_duration'] = rv_dict['{}_{}'.format(LabelUtteranceInfo.__tablename__, 'detect_duration')]
        vm['label_status'] = rv_dict['{}_{}'.format(LabelResult.__tablename__, 'label_status')]
        vms.append(vm)

    return PageResultSuccess(msg=u'项目关联语句列表', data=vms, page=rvs.page_view())


@api.route('/del-all-uttrs', methods=['POST'])
@auth.login_required
def lbproj_del_all_utterance():
    proj_id = LabelProjectIDForm().validate_for_api().proj_id.data
    form = UtteranceSearchForm().validate_for_api()

    q = db_v2.session.query(LabelResult, LabelUtteranceInfo).filter(
        LabelResult.is_deleted == 0,
        LabelUtteranceInfo.is_deleted == 0,
        LabelUtteranceInfo.request_id == LabelResult.request_id,
        LabelResult.proj_id == proj_id)

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

    with db_v2.auto_commit():
        for uttr_audio in uttr_audio_list:
            if uttr_audio.uttr_status != UtteranceStatusEnum.LABELED.value:
                uttr_audio.uttr_status = UtteranceStatusEnum.SELECTED.value
        for label_result, utterance_info in rvs:
            label_result.delete()
            if utterance_info.uttr_status != UtteranceStatusEnum.LABELED.value:
                utterance_info.uttr_status = UtteranceStatusEnum.SELECTED.value

    return DeleteSuccess(msg=u'项目全部语句解除关联成功')


@api.route('/del-uttrs', methods=['POST'])
@auth.login_required
def lbproj_del_utterance():
    form = LabelProjectUtteranceMapForm().validate_for_api()

    req_id_list = form.req_id_list.data

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

        rvs_part = db_v2.session.query(LabelResult, LabelUtteranceInfo).filter(
            LabelResult.proj_id == form.proj_id.data,
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

    with db_v2.auto_commit():
        for uttr_audio in uttr_audio_list:
            if uttr_audio.uttr_status != UtteranceStatusEnum.LABELED.value:
                uttr_audio.uttr_status = UtteranceStatusEnum.SELECTED.value
        for label_result, utterance_info in rvs:
            label_result.delete()
            if utterance_info.uttr_status != UtteranceStatusEnum.LABELED.value:
                utterance_info.uttr_status = UtteranceStatusEnum.SELECTED.value

    return DeleteSuccess(msg=u'项目语句解除关联成功')


@api.route('/set-all-uttrs', methods=['POST'])
@auth.login_required
def lbproj_set_all_utterance():
    # uttr
    label_project = LabelProject.query.filter_by(id=LabelProjectIDForm().validate_for_api().proj_id.data).first_or_404()

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

    rvs_uttr = q.all()
    logger.debug('{} length: {}'.format('rvs_uttr', len(rvs_uttr)))

    current_t = current_timestamp_sec()
    uttr_audio_list = []
    uttr_info_add_list = []
    uttr_info_list = []
    label_result_list = []
    for uttr_audio, uttr_access in rvs_uttr:
        uttr_info = LabelUtteranceInfo()
        if uttr_audio.uttr_status == UtteranceStatusEnum.SELECTED.value:
            uttr_info = LabelUtteranceInfo.query.filter_by(request_id=uttr_audio.request_id).first()

        if not uttr_info or not uttr_info.id:
            for v_key in uttr_audio.keys():
                if v_key in ['id', 'insert_time', 'is_deleted', ]:
                    continue
                setattr(uttr_info, v_key, getattr(uttr_audio, v_key, None))
            for v_key in uttr_access.keys():
                if v_key in ['id', 'insert_time', 'is_deleted', ]:
                    continue
                setattr(uttr_info, v_key, getattr(uttr_access, v_key, None))
            uttr_info.uttr_status = UtteranceStatusEnum.SELECTED.value
            uttr_info_add_list.append(uttr_info)
        else:
            uttr_info_list.append(uttr_info)

        uttr_audio_list.append(uttr_audio)

        label_result = LabelResult()
        label_result.request_id = uttr_info.request_id
        label_result.uttr_url = uttr_info.url
        label_result.uttr_result = uttr_info.result
        label_result.uttr_stt_time = datetime2timestamp(uttr_info.time)
        label_result.proj_id = label_project.id
        label_result.proj_code = label_project.proj_code
        label_result.proj_name = label_project.proj_name
        label_result.task_id = -1  # -1代表语句还没分配到任务
        label_result.create_time = current_t
        label_result_list.append(label_result)

    with db_v2.auto_commit():
        utterance_info_dict_list = [dict(utterance_info) for utterance_info in uttr_info_add_list]
        db_v2.session.execute(LabelUtteranceInfo.__table__.insert().prefix_with('IGNORE'), utterance_info_dict_list)

        # db_v2.session.bulk_save_objects(uttr_info_add_list)

    uttr_info_list = uttr_info_list + uttr_info_add_list
    logger.debug('{} length: {}'.format('uttr_info_list', len(uttr_info_list)))

    with db_v2.auto_commit():
        for uttr_audio in uttr_audio_list:
            uttr_audio.uttr_status = UtteranceStatusEnum.ASSIGNED_PROJ.value
        for uttr_info in uttr_info_list:
            uttr_info.uttr_status = UtteranceStatusEnum.ASSIGNED_PROJ.value
        db_v2.session.bulk_save_objects(label_result_list)

    return Success(msg=u'项目关联语句成功')


@api.route('/set-uttrs', methods=['POST'])
@auth.login_required
def lbproj_set_utterance():
    form = LabelProjectUtteranceMapForm().validate_for_api()

    label_project = LabelProject.query.filter_by(id=form.proj_id.data).first_or_404()

    req_id_list = form.req_id_list.data

    # 迁移web
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

    # 建立关联
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
                logger.debug('counter: {}'.format(select_in_loop_counter))
                break

            rvs_part = LabelUtteranceInfo.query.filter(
                LabelUtteranceInfo.request_id.in_(req_id_list[select_in_from:select_in_to])).all()
            uttr_info_list += rvs_part

            select_in_from = select_in_to
            select_in_to = select_in_from + select_in_step
            select_in_loop_counter += 1
        logger.debug('uttr_info_list length: {}'.format(len(uttr_info_list)))

    current_t = current_timestamp_sec()
    label_result_list = []
    for uttr_info in uttr_info_list:
        label_result = LabelResult()
        label_result.request_id = uttr_info.request_id
        label_result.uttr_url = uttr_info.url
        label_result.uttr_result = uttr_info.result
        label_result.uttr_stt_time = datetime2timestamp(uttr_info.time)
        label_result.proj_id = label_project.id
        label_result.proj_code = label_project.proj_code
        label_result.proj_name = label_project.proj_name
        label_result.task_id = -1  # -1代表语句还没分配到任务
        label_result.create_time = current_t
        label_result_list.append(label_result)

    with db_v2.auto_commit():
        db_v2.session.bulk_save_objects(label_result_list)
        for uttr_info in uttr_info_list:
            uttr_info.is_assigned = 1

    return Success(msg=u'项目关联语句成功')


@api.route('/choices-name', methods=['GET'])
@auth.login_required
def lbproj_choices_name():
    # TODO 权限
    rvs = db_v2.session.query(LabelProject.id, LabelProject.proj_name).filter_by().all()

    if not rvs:
        return ResultSuccess(msg=u'无项目数据', data=[])

    vms = []
    for id, proj_name in rvs:
        vm = dict(
            k=id,
            v=proj_name
        )
        vms.append(vm)

    choice_type = int(request.args.get('choice_type', 0) if not request.args.get('choice_type') == 'undefined' else 0)
    if choice_type == ChoicesExTypeEnum.TYPE_NEITHER.value:
        vms.append(dict(k=ChoicesExItemEnum.NEITHER.value, v=u'无参与项目'))
    elif choice_type == ChoicesExTypeEnum.TYPE_ALL.value:
        vms.insert(0, dict(k=ChoicesExItemEnum.ALL.value, v=u'全部项目'))
    elif choice_type == ChoicesExTypeEnum.TYPE_NEITHER_ALL.value:
        vms.insert(0, dict(k=ChoicesExItemEnum.ALL.value, v=u'全部项目'))
        vms.append(dict(k=ChoicesExItemEnum.NEITHER.value, v=u'无参与项目'))

    return ResultSuccess(msg=u'项目名称字典', data=vms)
