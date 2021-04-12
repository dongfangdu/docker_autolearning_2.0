# -*- coding: utf-8 -*-
import logging

from flask import g, request
from sqlalchemy import desc, func, distinct, or_

from app.libs.builtin_extend import namedtuple_with_defaults, current_timestamp_sec
from app.libs.enums import LabelUserMapRelTypeEnum, ChoicesExItemEnum
from app.libs.error_code import Success, DeleteSuccess, ResultSuccess, CreateSuccess, EditSuccess, PageResultSuccess
from app.libs.qpaginate import pager
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.v2.web.sysmgr import User, Role
from app.models.base import db_v2
from app.models.v2.web.label import LabelUserMap, LabelProject
from app.validators.base import PageForm
from app.validators.forms_v2 import PasswordForm, UserNicknameForm, UserSearchForm, UserEditForm, UserMapEditForm

api = Redprint('user')
logger = logging.getLogger(__name__)


@api.route('', methods=['POST'])
@auth.login_required
def user_add():
    form = UserNicknameForm().validate_for_api()
    user = User()

    with db_v2.auto_commit():
        form.populate_obj(user)
        user.password = form.secret.data
        user.create_time = current_timestamp_sec()
        db_v2.session.add(user)
    with db_v2.auto_commit():
        if len(form.proj_ids.data) > 0:
            label_user_map_list = []
            for proj_ids in form.proj_ids.data:
                label_user_map = LabelUserMap()
                label_user_map.uid = user.id
                label_user_map.rel_type = LabelUserMapRelTypeEnum.PROJECT.value
                label_user_map.rel_id = proj_ids
                label_user_map_list.append(label_user_map)
            db_v2.session.bulk_save_objects(label_user_map_list)

    vm = UserViewListItem()._asdict()
    vm = dict(zip(vm.keys(), [dict(vm, **user)[x] for x in vm.keys()]))
    role = Role.query.filter_by(id=user.rid).first()
    vm['rcode'] = role.rcode
    vm['rname'] = role.rname
    label_project_list = LabelProject.query.filter(LabelUserMap.rel_id == LabelProject.id,
                                                   LabelUserMap.rel_type == LabelUserMapRelTypeEnum.PROJECT.value,
                                                   LabelUserMap.uid == user.id).all()
    proj_name_list = [label_proj.proj_name for label_proj in label_project_list]
    proj_name = '无参与项目' if len(proj_name_list) == 0 else ', '.join(proj_name_list)
    vm['proj_name'] = '全部项目' if role.rcode == 'projmanager' else proj_name

    return CreateSuccess(msg='用户新增', data=vm)


@api.route('/del/<int:uid>', methods=['GET'])
@auth.login_required
def user_super_del(uid):
    with db_v2.auto_commit():
        user = User.query.filter_by(id=uid).first_or_404()
        user.delete()
    return DeleteSuccess(msg='用户删除')


UserViewListItemFields = ('id', 'account', 'nickname', 'rname', 'create_time')
UserViewListItem = namedtuple_with_defaults('UserViewListItem', UserViewListItemFields,
                                            default_values=(None,) * len(UserViewListItemFields))


@api.route('/list', methods=['POST'])
@auth.login_required
def user_list():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    form = UserSearchForm().validate_for_api()
    group_tmp = db_v2.session.query(LabelUserMap.uid.label('uid'),
                                    func.count(distinct(LabelUserMap.rel_id)).label('project_cnt'),
                                    func.group_concat(LabelProject.proj_name).label('project_names'),
                                    func.concat(',', func.group_concat(LabelProject.id), ',').label(
                                        'project_ids')).filter(
        LabelUserMap.is_deleted == 0,
        LabelUserMap.rel_type == LabelUserMapRelTypeEnum.PROJECT.value,
        LabelUserMap.rel_id == LabelProject.id).group_by(LabelUserMap.uid).subquery()

    q = db_v2.session.query(User, Role, group_tmp).order_by(desc(User.create_time), User.id).join(group_tmp,
                                                                                                  User.id == group_tmp.c.uid,
                                                                                                  isouter=True).filter(
        User.rid == Role.id)

    # 权限处理
    # print(g.user.scope)
    # g_user = User.query.filter_by(id=g.user.uid).first_or_404()
    scope = g.user.scope
    scope_list = [scope, ]
    if scope != 'superadmin':
        if scope == 'taskmanager':
            scope_list += ['taskoperator', ]
            # form.proj_id.data = g_user.proj_id
        if scope == 'projmanager':
            scope_list += ['taskmanager', 'taskoperator']
        q = q.filter(or_(Role.rcode.in_(scope_list), User.id == g.user.uid))

    if form.nickname.data:
        q = q.filter(User.nickname.like('%' + form.nickname.data + "%"))
    if form.rid.data:
        q = q.filter(Role.id == form.rid.data)
    if form.proj_id.data is not None and form.proj_id.data != '':
        # print form.proj_id.data
        if form.proj_id.data == ChoicesExItemEnum.NEITHER.value:
            q = q.filter(group_tmp.c.project_cnt == None, Role.rcode != 'projmanager')
        elif form.proj_id.data == ChoicesExItemEnum.ALL.value:
            q = q.filter(Role.rcode == 'projmanager')
        else:
            q = q.filter(group_tmp.c.project_ids.like('%,{},%'.format(form.proj_id.data)))

    q = q.filter(User.is_deleted == 0)

    rvs = pager(q, page=cur_page, per_page=per_page)

    vms = []
    for rv in rvs.items:
        rv_dict = {c: getattr(rv, c, None) for c in rv._fields}
        vm = UserViewListItem()._asdict()
        vm = dict(zip(vm.keys(), [dict(vm, **rv_dict['User'])[x] for x in vm.keys()]))
        vm['rcode'] = rv_dict['Role'].rcode
        vm['rname'] = rv_dict['Role'].rname
        proj_name = '无参与项目' if (not rv_dict['project_cnt'] or (rv_dict['project_cnt'] == 0)) else rv_dict[
            'project_names']
        vm['proj_name'] = '全部项目' if rv_dict['Role'].rcode == 'projmanager' else proj_name
        # vm['proj_name'] = '无参与项目' if (rv_dict['project_cnt'] == 0 or not rv_dict['project_cnt']) else rv_dict[
        #     'project_names']
        vms.append(vm)

    return PageResultSuccess(msg='用户列表', data=vms, page=rvs.page_view())


@api.route('/edit', methods=['POST'])
@auth.login_required
def user_edit():
    uid = g.user.uid
    user = User.query.filter_by(id=uid).first_or_404()
    form = UserEditForm().validate_for_api()

    # with db_v2.auto_commit():
    #     if form.nickname.data:
    #         user.nickname = form.nickname.data
    #     if form.telephone.data:
    #         user.telephone = form.telephone.data
    return EditSuccess()


@api.route('/edit-map', methods=['POST'])
@auth.login_required
def user_edit_map():
    # uid = g.user.uid
    # user = User.query.filter_by(id=uid).first_or_404()
    form = UserMapEditForm().validate_for_api()

    with db_v2.auto_commit():
        LabelUserMap.query.filter(LabelUserMap.uid == form.uid.data,
                                  LabelUserMap.rel_type == LabelUserMapRelTypeEnum.PROJECT.value).delete()
        if len(form.proj_ids.data) > 0:
            label_user_map_list = []
            for proj_ids in form.proj_ids.data:
                label_user_map = LabelUserMap()
                label_user_map.uid = form.uid.data
                label_user_map.rel_type = LabelUserMapRelTypeEnum.PROJECT.value
                label_user_map.rel_id = proj_ids
                label_user_map_list.append(label_user_map)
            db_v2.session.bulk_save_objects(label_user_map_list)
    return EditSuccess()


@api.route('', methods=['GET'])
@auth.login_required
def user_get():
    uid = g.user.uid
    user, role = db_v2.session.query(User, Role).filter_by(id=uid, rid=Role.id).first_or_404()
    vm = UserViewListItem()._asdict()
    vm = dict(zip(vm.keys(), [dict(vm, **user)[x] for x in vm.keys()]))
    vm['rcode'] = role.rcode
    vm['rname'] = role.rname
    vm['proj_code'] = ''
    vm['proj_name'] = ''
    return ResultSuccess(msg='个人用户信息', data=vm)  # 都有id，注意merge顺序


@api.route('/<int:uid>', methods=['GET'])
@auth.login_required
def user_super_get(uid):
    user, role = db_v2.session.query(User, Role).filter_by(id=uid, rid=Role.id).first_or_404()
    vm = UserViewListItem()._asdict()
    vm = dict(zip(vm.keys(), [dict(vm, **user)[x] for x in vm.keys()]))
    vm['rcode'] = role.rcode
    vm['rname'] = role.rname
    return ResultSuccess(msg=u'用户信息', data=vm)


@api.route('/change-pwd', methods=['POST'])
@auth.login_required
def user_change_pwd():
    uid = g.user.uid
    form = PasswordForm().validate_for_api()
    with db_v2.auto_commit():
        user = User.query.filter_by(id=uid).first_or_404()
        user.password = form.secret.data

    return Success(msg=u'修改密码成功')


@api.route('/reset-pwd/<int:uid>', methods=['GET'])
@auth.login_required
def user_super_reset_pwd(uid):
    with db_v2.auto_commit():
        user = User.query.filter_by(id=uid).first_or_404()
        user.password = '123456'
    return Success(msg=u'密码重设成功')


@api.route('/choices-tagger', methods=['GET'])
@auth.login_required
def user_list_tagger():
    q = db_v2.session.query(User.id, User.nickname).filter(
        User.is_deleted == 0,
        User.rid == Role.id
    )

    proj_id = request.args.get('proj_id')
    if not int(proj_id) == -1:
        q = q.filter(User.id == LabelUserMap.uid,
                     LabelUserMap.rel_type == LabelUserMapRelTypeEnum.PROJECT.value,
                     LabelUserMap.rel_id == proj_id)
        q = q.filter(Role.rcode == 'taskoperator')
    else:
        q = q.filter(Role.rgroup == 2)

    rvs = q.all()
    vms = []
    for id, nickname in rvs:
        vm = dict(
            k=id,
            v=nickname
        )
        vms.append(vm)
    return ResultSuccess(msg=u'标注人员列表', data=vms)
