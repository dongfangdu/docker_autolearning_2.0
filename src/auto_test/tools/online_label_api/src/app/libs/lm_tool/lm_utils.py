# -*- coding: utf-8 -*-
import os
import warnings

from app.libs.path_utils import get_resource_dir
from .srilm import initLM, readLM


class LMv1:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        default_lm = 'en_sample.lm'

        if (
                'LM_NGRAM_PATH' not in app.config
        ):
            warnings.warn('LM_NGRAM_PATH is set. Defaulting LM_NGRAM_PATH to "{}".'.format(default_lm))

        if (
                'LM_NGRAM_ORDER' not in app.config
        ):
            warnings.warn('LM_NGRAM_ORDER is set. Defaulting LM_NGRAM_ORDER to "{}".'.format(3))

        app.config.setdefault('LM_NGRAM_PATH', default_lm)
        app.config.setdefault('LM_NGRAM_ORDER', 3)

        ngram_order = app.config['LM_NGRAM_ORDER']
        self.lm = initLM(ngram_order)

        ngram_path = app.config['LM_NGRAM_PATH']
        if ngram_path == default_lm:
            ngram_path = os.path.join(os.path.dirname(__file__), ngram_path)

        if ngram_path[0] != '/':
            ngram_path = os.path.join(get_resource_dir(), ngram_path)

        if not os.path.exists(ngram_path):
            raise RuntimeError('Language model is not exist. Please set a correct value for LM_NGRAM_PATH.')
        readLM(self.lm, ngram_path)

        app.extensions['lm_ngram'] = self.lm
