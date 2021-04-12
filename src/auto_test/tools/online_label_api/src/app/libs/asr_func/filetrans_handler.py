# -*- coding: utf-8 -*-
import httplib
import json
import logging
import shutil
import traceback

import os
import time

from app.libs.builtin_extend import current_timestamp_sec
from app.libs.ng_utils import get_ng_ft_host, get_ng_redis_connection, get_ng_ft_logs_dir, get_ng_ft_data_tmp_dir, \
    get_ng_ft_docker_data_tmp_dir

logger = logging.getLogger(__name__)


class FileTransRestful:
    system_name = 'autolearning'

    def __init__(self, file_path, host=None, app_key=None, token=None, protocol='file'):
        self.task_id = None
        self.protocol = protocol
        if protocol == 'file':
            self.is_local = True
        else:
            self.is_local = False
        self.tmp_json = os.path.join(os.path.dirname(__file__), 'asrc_path.json')
        self.host = host or get_ng_ft_host()
        self.app_key = app_key or 'default'
        self.token = token or 'default'
        self.file_path = file_path
        self.file_link_template = '{}://{{}}/{{}}'.format(protocol)

    def submit_filetrans(self):
        url = 'http://' + self.host + '/stream/v1/filetrans'
        http_headers = {
            'Content-Type': 'application/json'
        }

        file_name = os.path.basename(self.file_path)
        file_dir = os.path.dirname(self.file_path)
        if self.is_local:
            ft_tmp_dir = get_ng_ft_data_tmp_dir(self.system_name, is_running=True)
            ft_docker_tmp_dir = get_ng_ft_docker_data_tmp_dir(self.system_name)
            ft_tmp_path = os.path.join(ft_tmp_dir, file_name)
            if not os.path.exists(ft_tmp_path):
                if not os.path.exists(self.file_path):
                    print u'文件丢失，原路径为{}'.format(self.file_path)
                    return
                shutil.move(self.file_path, ft_tmp_path)

            file_link = self.file_link_template.format(ft_docker_tmp_dir, file_name)
        else:
            file_link = self.file_link_template.format(file_dir, file_name)

        body = {'appkey': self.app_key, 'token': self.token, 'file_link': file_link}

        body = json.dumps(body)

        conn = httplib.HTTPConnection(self.host)
        conn.request(method='POST', url=url, body=body, headers=http_headers)

        response = conn.getresponse()

        body = response.read()

        try:
            body = json.loads(body)
            result = body['header']
            status_message = result['status_message']
            if 'SUCCESS' == status_message:
                self.task_id = result['task_id']

        except ValueError:
            print('The response is not json format string')

        conn.close()

    @staticmethod
    def wait_for_finished(task_id_list, sleep_epoch=2, timeout=None):
        _check_queue = task_id_list
        succ_task = []
        fail_task = []
        non_valid_task = []     # 包含非法task_id和超时的
        _timeout = timeout or 60 * 15

        cur_time = current_timestamp_sec()
        while True:
            # print len(_check_queue)
            if (current_timestamp_sec() - cur_time) > _timeout:
                print u"超时跳出"
                non_valid_task = non_valid_task+_check_queue
                break

            if len(_check_queue) < 1:
                break
            task_id = _check_queue.pop()
            result = FileTransRestful.get_redis_result(task_id)

            if not result:
                non_valid_task.append(task_id)
                continue

            status_text = result['status_text']

            if 'QUEUEING' == status_text or 'RUNNING' == status_text:
                _check_queue.append(task_id)
                time.sleep(sleep_epoch)
            elif 'SUCCESS_WITH_NO_VALID_FRAGMENT' == status_text or 'SUCCESS' == status_text:
                succ_task.append(task_id)
            else:
                fail_task.append(task_id)
        return succ_task, fail_task, non_valid_task

    @staticmethod
    def get_http_result(task_id, host=None, app_key=None, token=None):
        if not task_id:
            return None
        host = host or get_ng_ft_host()
        if not host:
            return None

        app_key = app_key or 'default'
        token = token or 'default'
        url = 'http://' + host + '/stream/v1/filetrans'
        url = url + '?appkey=' + app_key
        url = url + '&token=' + token
        url = url + '&task_id=' + task_id

        conn = httplib.HTTPConnection(host)

        conn.request(method='GET', url=url)
        response = conn.getresponse()
        body = response.read()
        if 200 != response.status:
            return None

        result = None
        try:
            result = json.loads(body)
        except ValueError:
            print(traceback.format_exc())

        conn.close()
        return result

    @staticmethod
    def get_redis_result(task_id):
        if not task_id:
            return None
        r_conn = get_ng_redis_connection()
        r_key = 'enterprise.nls.trans.task.result.{}'.format(task_id)
        r_value = r_conn.get(r_key)

        if not r_value:
            return None

        try:
            result = json.loads(r_value)
            return result
        except ValueError:
            print(traceback.format_exc())
            return None

    @staticmethod
    def get_redis_request(task_id):
        if not task_id:
            return None
        r_conn = get_ng_redis_connection()
        r_key = 'enterprise.nls.trans.task.request.{}'.format(task_id)
        r_value = r_conn.get(r_key)

        if not r_value:
            return None

        try:
            result = json.loads(r_value)
            return result
        except ValueError:
            print(traceback.format_exc())
            return None

    @staticmethod
    def get_redis_running(task_id):
        if not task_id:
            return None
        r_conn = get_ng_redis_connection()
        r_key = 'enterprise.nls.trans.task.running.log.{}'.format(task_id)
        r_value = r_conn.get(r_key)

        if not r_value:
            return None

        try:
            result = json.loads(r_value)
            return result
        except ValueError:
            print(traceback.format_exc())
            return None

    @staticmethod
    def get_ft_log_info(task_id):
        if not task_id:
            return None

        ft_logs_dir = get_ng_ft_logs_dir()
        ft_application_log = os.path.join(ft_logs_dir, 'application.log*')

        command = 'grep -h {} {}'.format(task_id, ft_application_log)

        import subprocess as sp
        child = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        streamdata = child.communicate()
        return_code = child.returncode
        if return_code != 0:
            print streamdata[1]
            return None

        return streamdata[0]

    @staticmethod
    def get_tmp_file_path(task_id):
        if not task_id:
            return None
        rq = FileTransRestful.get_redis_request(task_id)
        if not rq:
            return None

        file_link = rq.get('file_link')
        if not file_link:
            return None

        protocol, filepath = str(file_link).split('://', 1)
        file_full_path = None
        if protocol == 'file':
            file_rel_path = os.path.relpath(filepath, get_ng_ft_docker_data_tmp_dir(FileTransRestful.system_name))
            file_full_path = os.path.join(get_ng_ft_data_tmp_dir(FileTransRestful.system_name, is_running=True),
                                          file_rel_path)

        return file_full_path

    def register_file_flow(self):
        self.submit_filetrans()
        return self.task_id

# if __name__ == '__main__':
#     rq = FileTransRestful.get_redis_request('49eb8fc6e92f11e98003618e2bbdbf8e')
#     file_link = rq['file_link']
#     protocol, filepath = str(file_link).split('://', 1)
#     file_full_path = None
#     if protocol == 'file':
#         file_rel_path = os.path.relpath(filepath, get_ng_ft_docker_data_tmp_dir(FileTransRestful.system_name))
#         file_full_path = os.path.join(get_ng_ft_data_tmp_dir(FileTransRestful.system_name), file_rel_path)

# file_path = '192.168.106.170:7779/home/admin/online_label_data/audiosrc/2019/09/04/9305a61521134cf088940639920ae164.wav'
# file_path = '/home/admin/online_label_data/audiosrc/2019/09/04/9305a61521134cf088940639920ae164.wav'
# task_id = FileTransRestful(file_path=file_path, protocol='file').register_file_flow()
# print task_id
# pass
