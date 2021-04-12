# -*- coding:utf-8 -*-
import httplib
import jieba
import json
import os
from app.libs.lm_tool.srilm import howManyNgrams, getSentencePpl, readLM, initLM
from app import create_app
jieba_status = False

def cal_ppl_api(sentence, url='http://192.168.100.210:7800/api/vX/lmdemo/ppl'):
    #jieba.load_userdict("/home/user/linjr/auto_test/tools/common-seg-dict.txt")
    seg_result = jieba.cut(sentence, cut_all=jieba_status)
    seg_result = ' '.join(seg_result)
    httpHeaders = {'Content-Type': 'application/json'}
    body = {'sentence': seg_result}
    body = json.dumps(body)
    conn = httplib.HTTPConnection('192.168.100.210:7800')
    conn.request(method='POST', url=url, body=body, headers=httpHeaders)
    response = conn.getresponse()
    res_body = response.read()
    res_body = json.loads(res_body)
    ppl = res_body['data']['ppl']
    return ppl

def cal_ppl(sentence):
    seg_result = jieba.cut(sentence, cut_all=jieba_status)
    seg_result = ' '.join(seg_result)
    lm = Singleton.instance()
    ppl = getSentencePpl(lm, str(seg_result), len(str(seg_result).split(' ')))
    return ppl
	
class Singleton(object):
    def __init__(self):
        pass

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(cls, "lm"):   
            cls.lm = initLM(4)
            cls.app = create_app(os.getenv('FLASK_CONFIG') or 'default')
            cls.lm_path = cls.app.config['LM_NGRAM_PATH']
            readLM(cls.lm, cls.lm_path)
        return cls.lm

def precog(real_rtf, ppl):
    real_rtf = float(real_rtf)
    ppl = float(ppl)
    a = 17.527179057939385
    b = [0.00000000e+00, 2.69501141e+01, 2.19320633e-04, -4.95873464e+00, 2.49565061e-07, -4.63231231e-10]
    pre_wer = a + b[1]*real_rtf + b[2]*ppl + b[3]*real_rtf*real_rtf + b[4]*real_rtf*ppl + b[5]*ppl*ppl
    return pre_wer
	
if __name__ == '__main__':
    a = ['你好', '吃饭了吗', '哈哈哈']
    for i in a:
        ppl = cal_ppl(i)
