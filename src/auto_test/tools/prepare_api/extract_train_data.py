# coding=utf-8
import datetime
import json
import os
import random
import uuid

import pymysql


def gen_prepare_id():
    return str(uuid.uuid4()).replace('-', '')


class DataPrepare():
    def prepare_data(self, prepare_type):

        prepare_uuid = gen_prepare_id()
        conn, cursor = self.connect_sql()
        request_id = self.prepare_request_id()
        prepare_start_time = self.time_status()
        prepare_end_time = ''
        prepare_type = prepare_type
        prepare_status = 0
        prepare_data_path = ''
        sql = "insert into al_prepare_train_request_info(prepare_uuid,prepare_start_time,prepare_end_time,prepare_status,prepare_types,prepare_data_path) values('%s','%s','%s','%s','%s','%s')" % (
            prepare_uuid, prepare_start_time, prepare_end_time, prepare_status, prepare_type, prepare_data_path)
        cursor.execute(sql)
        conn.commit()

        data_size = 0
        request_id_reference = open('/home/user/lingq/auto_learning/data/txt/reference.txt', 'w')
        for i in request_id:
            sql = "select detect_duration from al_data_source where request_id='%s'" % (i[0])
            res = cursor.execute(sql)
            ret = cursor.fetchone()
            detect_duration = list(ret)
            if data_size <= 7397000:
                sql = "select result from al_data_source where request_id='%s'" % (i[0])
                res = cursor.execute(sql)
                ret = cursor.fetchone()
                result_list = list(ret)
                request_id_reference.write(i[0] + '\t' + str(result_list[0]) + '\n')
                sql = "select path from al_data_path_source where request_id='%s'" % (i[0])

                res = cursor.execute(sql)
                ret = cursor.fetchone()
                path_list = ret
                sql = "select id from al_data_path_source where request_id='%s'" % (i[0])
                res = cursor.execute(sql)
                data_id = cursor.fetchone()

                sql = "insert into al_prepare_train_data_info(repare_uuid,request_id,label_text,prepare_filepath,data_id) values('%s','%s','%s','%s','%s')" % (
                    prepare_uuid, i[0], result_list[0], path_list[0], data_id[0])
                cursor.execute(sql)
                conn.commit()
                os.system('cd %s;cp %s /home/user/lingq/auto_learning/data/wav/' % (
                    path_list[0].split('default')[0] + 'default', path_list[0]))
                data_size += detect_duration[0]
            else:
                conn, cursor = self.connect_sql()
                prepare_end_time = self.time_status()
                sql = "update al_prepare_train_request_info set prepare_data_path='%s' where prepare_uuid='%s'" % (
                    '/home/user/lingq/auto_learning/data/wav/', prepare_uuid)
                cursor.execute(sql)
                conn.commit()
                sql = "update al_prepare_train_request_info set prepare_status='%s' where prepare_uuid='%s'" % (
                    1, prepare_uuid)
                cursor.execute(sql)
                conn.commit()

            conn.close()

            res = dict(prepare_uuid=prepare_uuid)
            res_json = json.dumps(res)

            return res_json

    def _check_is_finished(self, prepare_uuid):
        conn, cursor = self.connect_sql()
        sql = "select prepare_status from al_prepare_train_request_info where prepare_uuid='%s'" % (prepare_uuid)
        cursor.execute(sql)
        i = cursor.fetchone()
        conn.close()
        # print(i)
        if i[0] == 1:
            return 1, '/home/user/lingq/auto_learning/data/wav/'
        else:
            return 0, ''

    def is_ready(self, prepare_uuid):

        prepare_status, mock_data_path = self._check_is_finished(prepare_uuid)

        res = dict(prepare_status=prepare_status, mock_data_path=mock_data_path)
        res_json = json.dumps(res)

        return res_json

    def time_status(self):

        prepare_start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return prepare_start_time

    def connect_sql(self):
        conn = pymysql.connect(host='192.168.106.170', port=3306, user='root', passwd='yjyjs123',
                               database='data_process')
        cursor = conn.cursor()
        return conn, cursor

    def prepare_request_id(self):
        conn, cursor = self.connect_sql()
        sql = "select request_id from al_data_source"
        res = cursor.execute(sql)
        ret = cursor.fetchall()
        request_id = list(ret)
        random.shuffle(request_id)
        return request_id



