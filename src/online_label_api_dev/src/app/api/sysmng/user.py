# -*- coding: utf-8 -*-
from flask import g
from sqlalchemy import or_

from app.libs.builtin_extend import namedtuple_with_defaults
from app.libs.error_code import Success, DeleteSuccess, ResultSuccess, CreateSuccess, EditSuccess, PageResultSuccess
from app.libs.qpaginate import pager
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db_v1
from app.models.v1.sysmng import User, Role
from app.models.v1.tagproj import TagProject
from app.validators.base import PageForm
from app.validators.forms_v1 import PasswordForm, UserNicknameForm, UserSearchForm, UserEditForm

api = Redprint('user')


@api.route('', methods=['POST'])
@auth.login_required
def user_add():
    form = UserNicknameForm().validate_for_api()
    user = User()
    with db_v1.auto_commit():
        form.populate_obj(user)
        user.password = form.secret.data
        db_v1.session.add(user)

    vm = UserViewListItem()._asdict()
    vm = dict(zip(vm.keys(), [dict(vm, **user)[x] for x in vm.keys()]))
    role = Role.query.filter_by(id=user.rid).first()
    vm['rcode'] = role.rcode
    vm['rname'] = role.rname
    tagproject = TagProject.query.filter_by(id=user.proj_id).first()
    vm['proj_name'] = '全部项目' if user.proj_id == 0 else tagproject.proj_name

    return CreateSuccess(msg='用户新增', data=vm)


@api.route('/del/<int:uid>', methods=['GET'])
@auth.login_required
def user_super_del(uid):
    with db_v1.auto_commit():
        user = User.query.filter_by(id=uid).first_or_404()
        user.delete()
    return DeleteSuccess(msg='用户删除')


UserViewListItemFields = ('id', 'account', 'nickname', 'rname', 'proj_id', 'create_time')
UserViewListItem = namedtuple_with_defaults('UserViewListItem', UserViewListItemFields,
                                            default_values=(None,) * len(UserViewListItemFields))


@api.route('/list', methods=['POST'])
@auth.login_required
def user_list():
    # print(g.user.scope)
    form = UserSearchForm().validate_for_api()
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    # if form.proj_id.data:
    #     proj_id = form.proj_id.data

    q = db_v1.session.query(User, Role).order_by(User.create_time.desc()).filter(User.rid == Role.id)

    g_user = User.query.filter_by(id=g.user.uid).first_or_404()
    scope = g.user.scope
    if scope != 'superadmin':
        role_id_list = [0, ]
        if scope == 'taskmanger':
            role_id_list += [5, ]
            form.proj_id.data = g_user.proj_id
        if scope == 'projmanger':
            role_id_list += [5, 4]
        q = q.filter(or_(Role.id.in_(role_id_list), User.id == g.user.uid))

    if form.nickname.data:
        q = q.filter(User.nickname.like('%' + form.nickname.data + "%"))
    if form.rid.data:
        q = q.filter(Role.id == form.rid.data)

    q = q.filter_by()

    q = q.add_entity(TagProject)
    if form.proj_id.data:
        q = q.join(TagProject, User.proj_id == TagProject.id, isouter=False).filter(User.proj_id == form.proj_id.data)
    else:
        q = q.join(TagProject, User.proj_id == TagProject.id, isouter=True)
    q = q.filter(or_(TagProject.is_deleted == 0, TagProject.is_deleted.is_(None)))

    rvs = pager(q, page=cur_page, per_page=per_page)

    vms = []
    for user, role, tagproject in rvs.items:
        vm = UserViewListItem()._asdict()
        vm = dict(zip(vm.keys(), [dict(vm, **user)[x] for x in vm.keys()]))
        vm['rcode'] = role.rcode
        vm['rname'] = role.rname
        vm['proj_name'] = '全部项目' if user.proj_id == 0 else tagproject.proj_name
        vms.append(vm)

    return PageResultSuccess(msg='用户列表', data=vms, page=rvs.page_view())


@api.route('/list-all', methods=['POST'])
@auth.login_required
def user_list_all():
    form = UserSearchForm().validate_for_api()

    q = db_v1.session.query(User, Role).order_by(User.id).filter(User.rid == Role.id)
    # TODO
    # 还有项目方面
    if form.nickname.data:
        q = q.filter(User.nickname.like('%' + form.nickname.data + "%"))
    if form.rid.data:
        q = q.filter(Role.id == form.rid.data)
    rvs = q.filter_by().all()

    vms = []
    for user, role in rvs:
        vm = UserViewListItem()._asdict()
        vm = dict(zip(vm.keys(), [dict(vm, **user)[x] for x in vm.keys()]))
        vm['rid'] = role.id
        vm['rcode'] = role.rcode
        vm['rname'] = role.rname
        vm['proj_code'] = '-'
        vms.append(vm)

    return ResultSuccess(msg='用户列表', data=vms)


@api.route('/edit', methods=['POST'])
@auth.login_required
def user_edit():
    uid = g.user.uid
    user = User.query.filter_by(id=uid).first_or_404()
    form = UserEditForm().validate_for_api()

    with db_v1.auto_commit():
        if form.nickname.data:
            user.nickname = form.nickname.data
        if form.telephone.data:
            user.telephone = form.telephone.data
    return EditSuccess()


def _get_simple_proj_info_by_id(proj_id):
    proj_code = '-'
    proj_name = '-'
    if proj_id == 0:
        proj_code = '全部项目'
        proj_name = '全部项目'
    else:
        rv = TagProject.query.with_entities(TagProject.proj_code, TagProject.proj_name).filter_by(id=proj_id).first()
        if rv:
            proj_code, proj_name = rv
    return proj_code, proj_name


@api.route('', methods=['GET'])
@auth.login_required
def user_get():
    uid = g.user.uid
    user, role = db_v1.session.query(User, Role).filter_by(id=uid, rid=Role.id).first_or_404()
    proj_code, proj_name = _get_simple_proj_info_by_id(user.proj_id)
    vm = UserViewListItem()._asdict()
    vm = dict(zip(vm.keys(), [dict(vm, **user)[x] for x in vm.keys()]))
    vm['rcode'] = role.rcode
    vm['rname'] = role.rname
    vm['proj_code'] = proj_code
    vm['proj_name'] = proj_name
    return ResultSuccess(msg='个人用户信息', data=vm)  # 都有id，注意merge顺序


@api.route('/<int:uid>', methods=['GET'])
@auth.login_required
def user_super_get(uid):
    user, role = db_v1.session.query(User, Role).filter_by(id=uid, rid=Role.id).first_or_404()
    proj_code, proj_name = _get_simple_proj_info_by_id(user.proj_id)
    vm = UserViewListItem()._asdict()
    vm = dict(zip(vm.keys(), [dict(vm, **user)[x] for x in vm.keys()]))
    vm['rcode'] = role.rcode
    vm['rname'] = role.rname
    vm['proj_code'] = proj_code
    vm['proj_name'] = proj_name
    return ResultSuccess(msg=u'用户信息', data=vm)


@api.route('/pw-change', methods=['POST'])
@auth.login_required
def user_pw_change():
    uid = g.user.uid
    form = PasswordForm().validate_for_api()
    with db_v1.auto_commit():
        user = User.query.filter_by(id=uid).first_or_404()
        user.password = form.secret.data

    return Success(msg=u'修改密码成功')


@api.route('/pw-reset/<int:uid>', methods=['GET'])
@auth.login_required
def user_super_pw_reset(uid):
    with db_v1.auto_commit():
        user = User.query.filter_by(id=uid).first_or_404()
        user.password = '123456'
    return Success(msg=u'密码重设成功')


@api.route('/choices-tagger', methods=['GET'])
@auth.login_required
def user_list_tagger():
    rvs = db_v1.session.query(User.id, User.nickname).filter(User.rid == Role.id,
                                                             Role.rcode == 'taskoperator').filter_by().all()
    vms = []
    for id, nickname in rvs:
        vm = dict(
            k=id,
            v=nickname
        )
        vms.append(vm)
    return ResultSuccess(msg=u'标注人员列表', data=vms)


@api.route('/choices-tagger/<int:proj_id>', methods=['GET'])
@auth.login_required
def user_list_tagger_by_proj_id(proj_id):
    rvs = db_v1.session.query(User.id, User.nickname).filter(
        User.rid == Role.id,
        Role.rcode == 'taskoperator',
        User.proj_id == proj_id).filter_by().all()
    vms = []
    for id, nickname in rvs:
        vm = dict(
            k=id,
            v=nickname
        )
        vms.append(vm)
    return ResultSuccess(msg=u'标注人员列表', data=vms)
