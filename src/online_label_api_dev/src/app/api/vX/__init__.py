# -*- coding: utf-8 -*-
from flask import Blueprint

from app.api.vX import speech_diar, lm_demo


def create_blueprint_vX():
    bp_vX = Blueprint('vX', __name__)

    speech_diar.api.register(bp_vX)
    lm_demo.api.register(bp_vX)

    return bp_vX
