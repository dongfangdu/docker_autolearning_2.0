# -*- coding: utf-8 -*-
import logging

from flask import current_app

from app.libs.error_code import Success
from app.libs.lm_tool.srilm import howManyNgrams, getSentencePpl
from app.libs.redprint import Redprint
from app.validators.forms_vX import SentenceForm

api = Redprint('lmdemo')  # speech_diarization 人声分离
logger = logging.getLogger(__name__)


@api.route('/test', methods=['GET'])
def lm_demo_test():
    lm = current_app.extensions['lm_ngram']
    print("   There are {} unigrams in this LM".format(howManyNgrams(lm, 1)))

    return Success(msg=u'成功')


@api.route('/ppl', methods=['POST'])
def lm_demo_ppl():
    sentence = SentenceForm().validate_for_api().sentence.data
    sentence = sentence.strip()
    lm = current_app.extensions['lm_ngram']

    print sentence
    sppl = getSentencePpl(lm, str(sentence), len(sentence.split(' ')))
    print("   ppl = {}".format(sppl))

    return Success(msg=u'成功')
