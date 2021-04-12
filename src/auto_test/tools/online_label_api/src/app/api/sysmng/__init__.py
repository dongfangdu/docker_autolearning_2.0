# -*- coding: utf-8 -*-

from flask import Blueprint

from app.api.sysmng import token, permission, region, user, role


def create_blueprint_sysmng():
    bp_sysmng = Blueprint('sysmng', __name__)

    user.api.register(bp_sysmng)
    role.api.register(bp_sysmng)
    permission.api.register(bp_sysmng)
    token.api.register(bp_sysmng)
    region.api.register(bp_sysmng)

    return bp_sysmng
