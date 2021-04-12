# -*- coding:utf-8 -*-
import httplib
import jieba
import json
jieba_status = False

def cal_ppl(sentence, url='http://192.168.108.197:7800/api/vX/lmdemo/ppl'):
    #jieba.load_userdict("/home/user/linjr/auto_test/tools/common-seg-dict.txt")
    seg_result = jieba.cut(sentence, cut_all=jieba_status)
    seg_result = ' '.join(seg_result)
    httpHeaders = {'Content-Type': 'application/json'}
    body = {'sentence': seg_result}
    body = json.dumps(body)
    conn = httplib.HTTPConnection('192.168.108.197:7800')
    conn.request(method='POST', url=url, body=body, headers=httpHeaders)
    response = conn.getresponse()
    res_body = response.read()
    res_body = json.loads(res_body)
    ppl = res_body['data']['ppl']
    return ppl

def precog(real_rtf, ppl):
    a = 17.527179057939385
    b = [0.00000000e+00, 2.69501141e+01, 2.19320633e-04, -4.95873464e+00, 2.49565061e-07, -4.63231231e-10]
    pre_wer = a + b[1]*real_rtf + b[2]*ppl + b[3]*real_rtf*real_rtf + b[4]*real_rtf*ppl + b[5]*ppl*ppl
    return pre_wer
    
if __name__ == '__main__':
    ppl = cal_ppl('你好吃饭了吗')
