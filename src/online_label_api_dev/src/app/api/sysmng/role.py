# -*- coding: utf-8 -*-
import time

from flask import jsonify

from app.libs.builtin_extend import namedtuple_with_defaults
from app.libs.error_code import Success, DeleteSuccess, ResultSuccess, ServerError, PageResultSuccess
from app.libs.qpaginate import pager
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db_v1
from app.models.v1.sysmng import Role, User, RolePermissionMap, Permission
from app.validators.base import PageForm
from app.validators.forms_v1 import RoleForm, RoleEditForm, IDForm, RolePermissionMapForm

api = Redprint('role')


@api.route('', methods=['POST'])
@auth.login_required
def role_add():
    form = RoleForm().validate_for_api()
    role = Role()
    with db_v1.auto_commit():
        form.populate_obj(role)
        db_v1.session.add(role)
    return ResultSuccess(msg=u'角色新增成功', data={'id': role.id, 'create_time': role.create_time})


@api.route('/<int:rid>', methods=['DELETE'])
@auth.login_required
def role_del(rid):
    with db_v1.auto_commit():
        role = Role.query.filter_by(id=rid).first_or_404()
        role.delete()

    return DeleteSuccess()


@api.route('/edit', methods=['POST'])
@auth.login_required
def role_edit():
    id = IDForm().validate_for_api().id.data
    role = Role.query.filter_by(id=id).first_or_404()

    form = RoleEditForm().validate_for_api()
    role_modified = Role()
    form.populate_obj(role_modified)

    with db_v1.auto_commit():
        for k, v in dict(role_modified).items():
            if v is not None:
                setattr(role, k, v)

    return ResultSuccess(data=role)


@api.route('/<int:rid>', methods=['GET'])
@auth.login_required
def role_get(rid):
    role = Role.query.filter_by(id=rid).first_or_404()
    return ResultSuccess(data=role)


@api.route('', methods=['GET'])
@auth.login_required
def role_get_all():
    role_objs = Role.query.filter_by().all()
    return ResultSuccess(msg=u'角色全部信息', data=role_objs)


RoleViewListItemFields = ('id', 'rname', 'rdesc')
RoleViewListItem = namedtuple_with_defaults('RoleViewListItem', RoleViewListItemFields,
                                            default_values=(None,) * len(RoleViewListItemFields))


@api.route('/list', methods=['POST'])
@auth.login_required
def role_list():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    role_objs = Role.query.filter_by().order_by(Role.id)
    rvs = pager(role_objs, page=cur_page, per_page=per_page)

    vms = []
    for role in rvs.items:
        vm = RoleViewListItem()._asdict()
        vm = dict(zip(vm.keys(), [dict(vm, **role)[x] for x in vm.keys()]))

        vms.append(vm)

    return PageResultSuccess(msg=u'角色列表', data=vms, page=rvs.page_view())


@api.route('/<rcode>', methods=['GET'])
@auth.login_required
def role_get_by_rcode(rcode):
    role = Role.query.filter_by(rcode=rcode).first_or_404()
    return jsonify(role)


@api.route('/set-perms', methods=['POST'])
def role_set_permission():
    form = RolePermissionMapForm().validate_for_api()

    # drop掉非法id
    pid_list = Permission.query.with_entities(Permission.id).filter(Permission.id.in_(form.pid_list.data)).all()

    current_t = int(time.time())  # 不是用add方法，初始化时current_time并没有调用父类Base的__init__方法
    r_p_map_list = []
    for pid, in pid_list:
        r_p_map = RolePermissionMap()
        r_p_map.rid = form.rid.data
        r_p_map.pid = pid
        r_p_map.create_time = current_t
        r_p_map_list.append(r_p_map)
    with db_v1.auto_commit():
        # RolePermissionMap.query.filter_by(rid=form.rid.data, with_deleted=True).delete()    # 批量删除
        RolePermissionMap.query.filter_by(rid=form.rid.data).update({'is_deleted': 1})      # 批量伪删除
        db_v1.session.bulk_save_objects(r_p_map_list)  # 批量添加

    # RolePermissionMap.query.filter_by(rid=form.rid.data)
    return Success(msg=u'角色关联权限成功')


@api.route('/choices-name', methods=['GET'])
@auth.login_required
def role_choices_name():
    role_objs = Role.query.filter_by().all()
    vms = []

    for role in role_objs:
        vms.append({'k': role.id, 'v': role.rname})

    return ResultSuccess(msg=u'角色名称字典', data=vms)


@api.route('/choices-code', methods=['GET'])
@auth.login_required
def role_choices_code():
    role_objs = Role.query.filter_by().all()
    vms = []

    for role in role_objs:
        vms.append({'k': role.id, 'v': role.rcode})

    return ResultSuccess(msg=u'角色编码字典', data=vms)


@api.route('/choices', methods=['GET'])
@auth.login_required
def role_choices():
    role_objs = Role.query.filter_by().all()
    vms = []

    for role in role_objs:
        vms.append({'k': role.id, 'v': {'rcode': role.rcode, 'rname': role.rname}})

    return ResultSuccess(msg=u'角色信息字典', data=vms)


def role_code_by_uid(uid):
    _, role = db_v1.session.query(User, Role).filter(User.rid == Role.id).filter_by(id=uid).first_or_404()
    return role.rcode


def role_code_by_user(user):
    if isinstance(user, User):
        return role_code_by_uid(user.id)
    else:
        raise ServerError()
