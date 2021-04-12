# -*- coding: utf-8 -*-

from flask import Blueprint

from app.api.v2 import lbtask, utterance, lbresult, stat, bgproc, asrc
from app.api.v2 import lbproj


def create_blueprint_v2():
    bp_v2 = Blueprint('v2', __name__)

    # demo.api.register(bp_v2)
    lbproj.api.register(bp_v2)
    lbtask.api.register(bp_v2)
    lbresult.api.register(bp_v2)
    utterance.api.register(bp_v2)
    stat.api.register(bp_v2)
    bgproc.api.register(bp_v2)
    asrc.api.register(bp_v2)

    return bp_v2
