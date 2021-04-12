# -*- coding: utf-8 -*-

from flask import Blueprint

from app.api.sysmgr import token, role, permission, user, region, plugin_mgr


def create_blueprint_sysmgr():
    bp_sysmgr = Blueprint('sysmgr', __name__)

    token.api.register(bp_sysmgr)
    role.api.register(bp_sysmgr)
    permission.api.register(bp_sysmgr)
    user.api.register(bp_sysmgr)
    region.api.register(bp_sysmgr)
    plugin_mgr.api.register(bp_sysmgr)


    return bp_sysmgr
