# -*- coding: utf-8 -*-

from flask import Blueprint

from app.api.v1 import tagproj
from app.api.v1 import tagtask
from app.api.v1 import tagresult
from app.api.v1 import utterance
from app.api.v1 import tagstat
from app.api.v1 import omutterance
from app.api.v1 import charts


def create_blueprint_v1():
    bp_v1 = Blueprint('v1', __name__)

    tagproj.api.register(bp_v1)
    tagtask.api.register(bp_v1)
    tagresult.api.register(bp_v1)
    utterance.api.register(bp_v1)
    tagstat.api.register(bp_v1)
    omutterance.api.register(bp_v1)
    charts.api.register(bp_v1)

    return bp_v1
