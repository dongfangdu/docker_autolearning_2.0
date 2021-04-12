import httplib
import json
# from configparser import ConfigParser
from ConfigParser import ConfigParser
from multiprocessing import Pool

# import http.client
import os
import pymysql
import time
from tqdm import tqdm
import generate_log
import time


class RestFul_RegToolOB():
    def __init__(self, host, wav_file, ini_path):
        self.Wav_File = wav_file
        self.Host = host
        self.appKey = "default"
        self.token = "default"
        self.FileLink = 'file:/home/admin/nls-filetrans/disk/' + self.Wav_File

        self.cwd_path = os.path.abspath(os.path.dirname(__file__))
        self._ini_path = os.path.join(self.cwd_path, '..', 'cfg', ini_path)
        self.cf = ConfigParser()
        self.cf.read(self._ini_path)
        #host = self.cf.get('TestSQL', 'host')
	
    def submitFileTransRequest(self):
        vocabulary_id = self.cf.get('Models', 'vocabulary_id')
        customization_id = self.cf.get('Models', 'customization_id')
        class_vocabulary_id = self.cf.get('Models', 'class_vocabulary_id')
        url = 'http://' + self.Host + '/stream/v1/filetrans'
        httpHeaders = {
            'Content-Type': 'application/json'
        }
        body = {'appkey': self.appKey, 'token': self.token, 'file_link': self.FileLink}
        if vocabulary_id != "":
            body['vocabulary_id'] = vocabulary_id
        if customization_id != "":
            body['customization_id'] = customization_id
        if class_vocabulary_id != "":
            body['class_vocabulary_id'] = class_vocabulary_id
        body = json.dumps(body)
        #print('The POST request body content: ' + body)
        conn = httplib.HTTPConnection(self.Host)
        conn.request(method='POST', url=url, body=body, headers=httpHeaders)
        response = conn.getresponse()
        #print('Response status: %s, Response reason: %s' % (response.status, response.reason))
        body = response.read()
        #print('Request Result: ' + str(body))
        taskId = None
        try:
            body = json.loads(body)
            result = body['header']
            statusMessage = result['status_message']
            if 'SUCCESS' == statusMessage:
                taskId = result['task_id']
        except ValueError:
            pass
            # print('The response is not json format string')
        conn.close()
        return taskId

    def getFileTransResult(self, taskid):
        #taskId = self.submitFileTransRequest()
        url = 'http://' + self.Host + '/stream/v1/filetrans'
        url = url + '?appkey=' + self.appKey
        url = url + '&token=' + self.token
        url = url + '&task_id=' + taskid
        conn = httplib.HTTPConnection(self.Host)
        self.result = None
        res_text = ''
        while True:
            conn.request(method='GET', url=url)
            response = conn.getresponse()
            # print('Response status: %s, Response reason: %s' % (response.status, response.reason))
            body = response.read()
            # print('Recognized Result: ' + str(body))
            # print(response.status)
            if response.status == 200:
                rootObj = json.loads(body)
                # print(rootObj)
                headerObj = rootObj['header']
                statusMessage = headerObj['status_message']		
                # print(statusMessage)
                if statusMessage == 'SUCCESS':
                    self.result = rootObj['payload']
                    # print(self.result)
                    # print(taskid)
                    if self.result == {}:
                        res_text += ''
                    else:
                        for i in range(len(self.result['sentences'])):
                            if i == 0:
                                res_text += self.result['sentences'][i]['text']
                            else:
                                res_text += ''
                                res_text += self.result['sentences'][i]['text']
                            # print(self.result['sentences'][i])
                            # print(res_text)
                    break
                elif statusMessage == 'SUCCESS_WITH_NO_VALID_FRAGMENT':
                    res_text += '~'
                    break
                elif statusMessage == 'RUNNING' or statusMessage == 'QUEUEING': 
                    continue
                else:
                    print('The response is not json format string')
                    break
            else:
                res_text += 'response.status != 200'
                break
        conn.close()
        # print('='*30)
        # print(self.result)
        # print('='*30)
        return res_text

def to_sql(ini_path):
    cwd_path = os.path.abspath(os.path.dirname(__file__))
    _ini_path = os.path.join(cwd_path, '..', 'cfg', ini_path)
    cf = ConfigParser()
    cf.read(_ini_path)
    host = cf.get('TestSQL', 'host')
    port = cf.get('TestSQL', 'port')
    user = cf.get('TestSQL', 'user')
    passwd = cf.get('TestSQL', 'passwd')
    db = cf.get('TestSQL', 'db')
    table = cf.get('TestSQL', 'temp_table')
    engine_path = cf.get('Engine', 'engine').split(':')[1]
    pos_host = cf.get('EngineServer', 'host') + ':8101'
    conn = pymysql.Connect(user=user, password=passwd, port=int(port), host=host, db=db, charset="utf8")
    cursor = conn.cursor()
    req_task_id = {}
    for file in os.listdir('%s/service/data/servicedata/nls-filetrans' %(engine_path)):
        taskid = RestFul_RegToolOB(pos_host, file, ini_path).submitFileTransRequest()
        wav_name = file.split('.')[0]
        req_task_id['%s'%(wav_name)] = taskid
    pbar = tqdm(total=len(os.listdir('%s/service/data/servicedata/nls-filetrans' %(engine_path))), desc='test progress')
    for request_id, task_id in req_task_id.items():
        res_text = RestFul_RegToolOB(pos_host, file, ini_path).getFileTransResult(task_id)
        sql = "update %s set task_id='%s',res_text='%s' where request_id='%s'" % (table, task_id, res_text, request_id)
        cursor.execute(sql)
        pbar.update(1)
    pbar.close()
    cursor.close()
    conn.commit()
    conn.close()


if __name__ == '__main__':
    try:
        to_sql('config.ini')
        generate_log.logger.info("test successful!")
    except Exception as exp:
        generate_log.logger.error("test failed!")
        generate_log.logger.error(exp.message)


