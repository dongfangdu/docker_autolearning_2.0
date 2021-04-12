# -*- coding: utf-8 -*-
import logging

import flask_httpauth
import time
from flask import current_app

from app.libs.builtin_extend import namedtuple_with_defaults, get_decorators
from app.libs.error_code import CreateSuccess, DeleteSuccess, EditSuccess, PageResultSuccess, ResultSuccess, Success
from app.libs.qpaginate import pager
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db_v2
from app.models.v2.web.sysmgr import Permission
from app.validators.base import PageForm
from app.validators.forms_v2 import PermissionForm, IDForm, PermissionEditForm

api = Redprint('perm')
logger = logging.getLogger(__name__)


@api.route('', methods=['POST'])
@auth.login_required
def permission_add():
    form = PermissionForm().validate_for_api()
    permission = Permission()
    with db_v2.auto_commit():
        form.populate_obj(permission)
        permission.create_time = int(time.time())
        db_v2.session.add(permission)

    vm = PermissionViewListItem()._asdict()
    vm = dict(zip(vm.keys(), [dict(vm, **permission)[x] for x in vm.keys()]))

    return CreateSuccess(msg=u'权限创建成功', data=vm)


@api.route('/del/<int:pid>', methods=['GET'])
@auth.login_required
def permission_del(pid):
    with db_v2.auto_commit():
        permission = Permission.query.filter_by(id=pid).first_or_404()
        permission.delete()
    return DeleteSuccess()


@api.route('/edit', methods=['POST'])
@auth.login_required
def permission_edit():
    id = IDForm().validate_for_api().id.data
    permission = Permission.query.filter_by(id=id).first_or_404()

    form = PermissionEditForm().validate_for_api()

    with db_v2.auto_commit():
        if form.pname.data:
            permission.pname = form.pname.data
        if form.presource.data:
            permission.presource = form.presource.data
    return EditSuccess(msg=u'权限修改成功')


PermissionViewListItemFields = ('id', 'pname', 'presource', 'create_time')
PermissionViewListItem = namedtuple_with_defaults('PermissionViewListItem', PermissionViewListItemFields,
                                                  default_values=(None,) * len(PermissionViewListItemFields))


@api.route('/list', methods=['POST'])
@auth.login_required
def permission_list():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    permssion_objs = Permission.query.filter_by().order_by(Permission.insert_time.desc())
    rvs = pager(permssion_objs, page=cur_page, per_page=per_page)

    vms = []
    for permission in rvs.items:
        vm = PermissionViewListItem()._asdict()
        vm = dict(zip(vm.keys(), [dict(vm, **permission)[x] for x in vm.keys()]))

        vms.append(vm)

    return PageResultSuccess(msg=u'权限列表', data=vms, page=rvs.page_view())


@api.route('/choices-name', methods=['GET'])
@auth.login_required
def permission_choices_name():
    permission_objs = Permission.query.filter_by().order_by(Permission.pname).all()
    vms = []

    for permission in permission_objs:
        vms.append({'k': permission.id, 'v': permission.pname})

    return ResultSuccess(msg=u'权限名称字典', data=vms)


def check_has_auth(function):
    cls_list = []
    for i in get_decorators(function):
        cls_list.append(i.__class__)
    return flask_httpauth.HTTPBasicAuth in cls_list


@api.route('/list-url-map', methods=['GET'])
def permission_list_url_map():
    links = []
    adapter = current_app.url_map.bind('v2')

    # for cell in permission_choices_name.func_closure:
    #     print getattr(cell, 'cell_contents', None)
    # if permission_list_url_map.func_closure:
    #     for cell in permission_list_url_map.func_closure:
    #         print getattr(cell, 'cell_contents', None)

    # print check_has_auth(permission_choices_name)
    # print check_has_auth(permission_list_url_map)

    # print adapter
    for rule in current_app.url_map.iter_rules():
        if 'v2' in rule.rule:
            # print rule, rule.methods, rule.defaults, rule.arguments
            if not check_has_auth(current_app.view_functions[rule.endpoint]):
                print rule.endpoint, current_app.view_functions[rule.endpoint].__doc__

    return Success(msg=u'')
