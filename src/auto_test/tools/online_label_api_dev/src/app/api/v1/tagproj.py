# -*- coding: utf-8 -*-
import time
from datetime import datetime
from flask import g
from operator import and_
from sqlalchemy import desc, and_

from app.api.sysmng.region import _region_fullname
from app.libs.builtin_extend import namedtuple_with_defaults, datetime2timestamp
from app.libs.error_code import DeleteSuccess, ResultSuccess, CreateSuccess, PageResultSuccess, EditSuccess, Success
from app.libs.qpaginate import pager
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db_v1
from app.models.v1.sysmng import User, Region
from app.models.v1.tagfile import Utterance, UtteranceAccess
from app.models.v1.tagproj import TagProject, TagResult
from app.validators.base import PageForm
from app.validators.forms_v1 import TagProjectForm, TagProjectSearchForm, IDForm, TagProjectEditForm, \
    TagProjectUtteranceMapForm, TagProjectIDForm, UtteranceRefSearchForm

api = Redprint('tagproj')


@api.route('', methods=['POST'])
@auth.login_required
def tagproj_add():
    form = TagProjectForm().validate_for_api()

    proj_cnt_by_region = TagProject.query.filter_by(with_deleted=True).count()
    project_code = 'TPJ{}'.format(str(proj_cnt_by_region + 1).zfill(3))
    uid = g.user.uid

    tag_project = TagProject()
    with db_v1.auto_commit():
        form.populate_obj(tag_project)
        tag_project.proj_code = project_code
        tag_project.create_uid = uid

        db_v1.session.add(tag_project)

    vm = TagProjectViewListItem()._asdict()
    vm = dict(zip(vm.keys(), [dict(vm, **tag_project)[x] for x in vm.keys()]))
    user = User.query.filter_by(id=tag_project.create_uid).first()
    vm['creator_name'] = user.nickname
    vm['region_name'] = _region_fullname(tag_project.region_id)
    return CreateSuccess(msg=u'项目新增成功', data=vm)


@api.route('/<int:oid>', methods=['GET'])
@auth.login_required
def tagproj_get(oid):
    tagproject = TagProject.query.filter_by(id=oid).first_or_404()

    vm = TagProjectViewListItem()._asdict()
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
def tagproj_del(oid):
    with db_v1.auto_commit():
        tag_project = TagProject.query.filter_by(id=oid).first_or_404()
        tag_project.delete()
        TagResult.query.filter(TagResult.proj_id == oid).filter_by().update({'is_deleted': 1})

    return DeleteSuccess(msg=u'项目删除成功')


TagProjectViewListItemFields = ('id', 'proj_code', 'proj_name', 'proj_desc', 'create_time', 'region_id')
TagProjectViewListItem = namedtuple_with_defaults('TagProjectViewListItem', TagProjectViewListItemFields,
                                                  default_values=(None,) * len(TagProjectViewListItemFields))


@api.route('/list', methods=['POST'])
@auth.login_required
def tagproj_list():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    form = TagProjectSearchForm().validate_for_api()
    q = db_v1.session.query(TagProject, User).order_by(TagProject.create_time.desc()).filter(
        TagProject.create_uid == User.id, TagProject.is_deleted == 0, User.is_deleted == 0)
    if form.proj_code.data:
        q = q.filter(TagProject.proj_code.like('%' + form.proj_code.data + "%"))
    if form.proj_name.data:
        q = q.filter(TagProject.proj_name.like('%' + form.proj_name.data + "%"))
    # TODO
    # 地域搜索（实现偏糟糕）
    region_id_prefix = ''
    if form.province_id.data:
        region_id_prefix = str(form.province_id.data)[:3]
    if form.city_id.data:
        region_id_prefix = str(form.city_id.data)[:4]
    if form.county_id.data:
        region_id_prefix = str(form.county_id.data)
    if region_id_prefix:
        q = q.filter(TagProject.region_id.like(region_id_prefix + '%'))
    q = q.filter_by()
    rvs = pager(q, page=cur_page, per_page=per_page)

    vms = []
    for tagproj, user in rvs.items:
        vm = TagProjectViewListItem()._asdict()
        vm = dict(zip(vm.keys(), [dict(vm, **tagproj)[x] for x in vm.keys()]))
        vm['creator_name'] = user.nickname
        vm['region_name'] = _region_fullname(tagproj.region_id)
        vms.append(vm)

    return PageResultSuccess(msg=u'标注项目列表', data=vms, page=rvs.page_view())


@api.route('/edit', methods=['POST'])
@auth.login_required
def tagproj_edit():
    id = IDForm().validate_for_api().id.data
    tagproj = TagProject.query.filter_by(id=id).first_or_404()
    form = TagProjectEditForm().validate_for_api()

    with db_v1.auto_commit():
        if form.proj_name.data:
            tagproj.proj_name = form.proj_name.data
        if form.proj_desc.data:
            tagproj.proj_desc = form.proj_desc.data
        if form.region_id.data:
            tagproj.region_id = form.region_id.data
    return EditSuccess(msg=u'项目信息修改成功')


@api.route('/del-all-uttrs', methods=['POST'])
@auth.login_required
def tagproj_del_all_uttrs():
    form = TagProjectIDForm().validate_for_api()

    q = db_v1.session.query(TagResult, Utterance, UtteranceAccess.time.label('stt_time')).filter(
        TagResult.request_id == Utterance.request_id, TagResult.request_id == UtteranceAccess.request_id).filter_by(
        proj_id=form.proj_id.data)

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

    q_final = []
    for q_item in q.all():
        q_items = q_item[:2]
        q_final.append(q_items)

    with db_v1.auto_commit():
        for tag_result, utterance in q_final:
            tag_result.delete()
            utterance.is_assigned = 0

    return DeleteSuccess(msg=u'项目全部语句解除关联成功')


@api.route('/del-uttrs', methods=['POST'])
@auth.login_required
def tagproj_del_uttrs():
    form = TagProjectUtteranceMapForm().validate_for_api()

    req_id_list = form.req_id_list.data

    if len(req_id_list) > 0:
        # TODO 不能用in sql
        rvs = db_v1.session.query(TagResult, Utterance).filter(TagResult.request_id == Utterance.request_id,
                                                               TagResult.request_id.in_(req_id_list)).filter_by(
            proj_id=form.proj_id.data).all()
        with db_v1.auto_commit():
            for tag_result, utterance,  in rvs:
                tag_result.delete()
                utterance.is_assigned = 0

    return DeleteSuccess(msg=u'项目语句解除关联成功')

@api.route('/list-uttrs', methods=['POST'])
@auth.login_required
def tagproj_list_utterance():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    form = TagProjectIDForm().validate_for_api()
    q = db_v1.session.query(TagResult, Utterance, UtteranceAccess.time.label('stt_time'),
                            UtteranceAccess.detect_duration.label('detect_duration')).filter(
        TagResult.request_id == Utterance.request_id, TagResult.request_id == UtteranceAccess.request_id).filter_by(
        proj_id=form.proj_id.data)

    if form.tag_status.data is not None and form.tag_status.data != '':
        q = q.filter(and_(TagResult.tag_status == form.tag_status.data, Utterance.is_assigned == 1))
    if form.stt_time_left.data and form.stt_time_right.data != '':
        q = q.filter(UtteranceAccess.time >= datetime.fromtimestamp(form.stt_time_left.data))
    if form.stt_time_right.data and form.stt_time_right.data != '':
        q = q.filter(UtteranceAccess.time <= datetime.fromtimestamp(form.stt_time_right.data))

    if form.num1.data is not None and form.num1.data != '':
        num_left = int(form.num1.data) - 1
        if form.num2.data is not None and form.num2.data !='':
            num_right = int(form.num2.data) - int(form.num1.data) + 1
            q = q.order_by(desc(UtteranceAccess.time)).limit(num_right).offset(num_left)
        else:
            q = q.order_by(desc(UtteranceAccess.time)).offset(num_left)
    else :
        if form.num2.data is not None and form.num2.data != '':
            num_right = int(form.num2.data)
            q = q.order_by(desc(UtteranceAccess.time)).limit(num_right)
        else :
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
        vm['tag_status'] = rv_dict['tag_result_tag_status']
        vms.append(vm)

    return PageResultSuccess(msg=u'项目关联语句列表', data=vms, page=rvs.page_view())


@api.route('/set-all-uttrs', methods=['POST'])
@auth.login_required
def tagproj_set_all_uttrs():
    uttr_form = UtteranceRefSearchForm().validate_for_api()

    q = db_v1.session.query(Utterance).filter(
        Utterance.request_id == UtteranceAccess.request_id,
        Utterance.is_deleted == 0, Utterance.is_assigned == 0)
    if uttr_form.stt_time_left.data:
        q = q.filter(UtteranceAccess.time >= datetime.fromtimestamp(uttr_form.stt_time_left.data))
    if uttr_form.stt_time_right.data:
        q = q.filter(UtteranceAccess.time <= datetime.fromtimestamp(uttr_form.stt_time_right.data))

    if uttr_form.num1.data is not None and uttr_form.num1.data != '':
        num_left = int(uttr_form.num1.data) - 1
        if uttr_form.num2.data is not None and uttr_form.num2.data != '':
            num_right = int(uttr_form.num2.data) - int(uttr_form.num1.data) + 1
            q = q.order_by(desc(UtteranceAccess.time)).limit(num_right).offset(num_left)
        else:
            q = q.order_by(desc(UtteranceAccess.time)).offset(num_left)
    else:
        if uttr_form.num2.data is not None and uttr_form.num2.data != '':
            num_right = int(uttr_form.num2.data)
            q = q.order_by(desc(UtteranceAccess.time)).limit(num_right)
        else:
            q = q.order_by(desc(UtteranceAccess.time))

    proj_id = TagProjectUtteranceMapForm().validate_for_api().proj_id.data
    current_t = int(time.time())
    tag_result_list = []

    for utterance in q.all():
        tag_result = TagResult()
        tag_result.request_id = utterance.request_id
        tag_result.proj_id = proj_id
        tag_result.task_id = -1  # -1代表语句还没分配到任务
        tag_result.create_time = current_t
        tag_result_list.append(tag_result)

    with db_v1.auto_commit():
        db_v1.session.bulk_save_objects(tag_result_list)
        for utterance in q.all():
            utterance.is_assigned = 1

    return Success(msg=u'项目关联语句成功')


@api.route('/set-uttrs', methods=['POST'])
@auth.login_required
def tagproj_set_utterance():
    form = TagProjectUtteranceMapForm().validate_for_api()

    req_id_list = form.req_id_list.data

    # drop掉非法req_id
    utterance_list = Utterance.query.with_entities(Utterance).filter(
        Utterance.request_id.in_(req_id_list)).all()

    current_t = int(time.time())
    tag_result_list = []
    for utterance in utterance_list:
        tag_result = TagResult()
        tag_result.request_id = utterance.request_id
        tag_result.proj_id = form.proj_id.data
        tag_result.task_id = -1  # -1代表语句还没分配到任务
        tag_result.create_time = current_t
        tag_result_list.append(tag_result)

    with db_v1.auto_commit():
        db_v1.session.bulk_save_objects(tag_result_list)
        for utterance in utterance_list:
            utterance.is_assigned = 1

    return Success(msg=u'项目关联语句成功')


@api.route('/choices-name', methods=['GET'])
@auth.login_required
def tagproj_choices_name():
    rvs = db_v1.session.query(TagProject.id, TagProject.proj_name).filter_by().all()

    if not rvs:
        return ResultSuccess(msg=u'无项目数据', data=[])

    vms = []
    for id, proj_name in rvs:
        vm = dict(
            k=id,
            v=proj_name
        )
        vms.append(vm)

    return ResultSuccess(msg=u'项目名称字典', data=vms)
