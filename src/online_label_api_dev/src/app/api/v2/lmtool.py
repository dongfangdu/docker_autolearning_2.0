# -*- coding:utf-8 -*-
import logging

from app.libs.redprint import Redprint

api = Redprint('lmtool')
logger = logging.getLogger(__name__)


@api.route('/calc-ppl', methods=['GET'])
def lmtool_calculate_perplexity():
    pass
