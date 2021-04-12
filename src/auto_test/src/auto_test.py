# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 14:20:10 2019

@author: 123
"""
import os
import sys
from tqdm import tqdm
import pandas as pd
import pymysql
from ConfigParser import ConfigParser
import generate_log
#cwd_path = os.path.abspath(os.path.dirname(__file__))
#sys.path.append('%s/../tools/online_label_api/src' %(cwd_path))
sys.path.append('/home/user/linjr/online_label_api_dev/src')
from local_api.data_prepare import DataPrepare
import prepare_test_data
import replace_model
import restfule_class
import move_log
import parse_log_to_mysql
import calculate_to_mysql
import report
import recover
import modify_conf
import json
from multiprocessing import Pool
import paramiko
import uuid
import time


class cycle_test():
    def __init__(self, ini_path):
        self.cwd_path = os.path.abspath(os.path.dirname(__file__))
        self.ini_path = os.path.join(self.cwd_path, '..', 'cfg', ini_path)
        self.cf = ConfigParser()
        self.cf.read(self.ini_path)
        self.test_host = self.cf.get('TestSQL', 'host')
        self.test_port = self.cf.get('TestSQL', 'port')
        self.test_user = self.cf.get('TestSQL', 'user')
        self.test_passwd = self.cf.get('TestSQL', 'passwd')
        self.test_db = self.cf.get('TestSQL', 'db')
        self.test_temp_table = self.cf.get('TestSQL', 'temp_table')
        self.test_overall_table = self.cf.get('TestSQL', 'overall_table')
        self.test_loop_counter_limit = self.cf.get('Testpara', 'countlimit')
        self.time_sleep = self.cf.get('Testpara', 'timesleep')

    def get_model(self):
        host = self.cf.get('TrainSQL', 'host')
        port = self.cf.get('TrainSQL', 'port')
        user = self.cf.get('TrainSQL', 'user')
        passwd = self.cf.get('TrainSQL', 'passwd')
        db = self.cf.get('TrainSQL', 'db')
        request_table = self.cf.get('TrainSQL', 'request_table')
        model_table = self.cf.get('TrainSQL', 'model_table')
        conn = pymysql.Connect(user=user, password=passwd, port=int(port), host=host, db=db, charset="utf8")
        conn_ = pymysql.Connect(user=user, password=passwd, port=int(port), host=host, db=self.test_db, charset="utf8")
        cur = conn.cursor()
        # cur.execute(
        #     'select model_uuid, model_url, corpus_uuid, init_model_url from %s a inner join %s b on a.train_uuid=b.train_uuid \
        #     where a.train_switch_mode=a.train_status and a.is_deleted != 1 and model_uuid not in (select model_uuid from %s.%s)' \
        #     % (request_table, model_table, self.test_db, self.test_overall_table))
        cur.execute(
            'select model_uuid, model_url, corpus_uuid, init_model_url from %s a inner join %s b on a.train_uuid=b.train_uuid \
            where (a.train_status = 3327 or a.train_status = 12288) and a.is_deleted != 1 and model_uuid not in (select model_uuid from %s.%s)' \
            % (request_table, model_table, self.test_db, self.test_overall_table))
        data = cur.fetchall()
        tables = pd.DataFrame(list(data), columns=['model_uuid', 'model_url', 'corpus_uuid', 'init_model_url'])
        # tab = tables.iloc[-1]
        model_uuid_list, model_save_path_list, prepare_id_list, init_model_list = list(tables['model_uuid']), \
                        list(tables['model_url']), list(tables['corpus_uuid']), list(tables['init_model_url'])
        cur_ = conn_.cursor()
        cur_.execute(
            'select model_uuid from %s.%s' % (self.test_db, self.test_overall_table))
        data_ = cur_.fetchall()
        tested_model_list = list(pd.DataFrame(list(data_), columns=['tested_model_list'])['tested_model_list'])
        if len(init_model_list) != 0 and 'init_model' not in tested_model_list:
            model_uuid_list.insert(0, 'init_model')
            model_save_path_list.insert(0, '%s' % (init_model_list[0]))
            prepare_id_list.insert(0, 'init_prepare_id')
        cur_.close()
        cur.close()
        conn.close()
        conn_.close()
        # print(model_uuid_list, model_save_path_list, prepare_id_list)
        return model_uuid_list, model_save_path_list, prepare_id_list

    def get_model_path(self):
        ip = self.cf.get('RemoteServer', 'host')
        port = self.cf.get('RemoteServer', 'port')
        user = self.cf.get('RemoteServer', 'user')
        passwd = self.cf.get('RemoteServer', 'passwd')
        # ip,port,user,passwd = parse_xml.server_info(xml_path)
        remote_connection = paramiko.Transport((ip, int(port)))
        remote_connection.connect(username=user, password=passwd)
        sftp = paramiko.SFTPClient.from_transport(remote_connection)        
        return sftp

    def test(self):
        # test_data_uuid = json.loads(data_prepare.DataPrepare().prepare_data(prepare_type=2))['prepare_uuid']
        # print(test_data_uuid)
        # res = json.loads(data_prepare.DataPrepare().is_ready(test_data_uuid))
        # print(res)
        dp = DataPrepare()
        while True:
            dp.prepare_data(prepare_type=4)
            time.sleep(float(self.time_sleep))
            conn_ = pymysql.Connect(user=self.test_user, password=self.test_passwd, port=int(self.test_port), \
                                    host=self.test_host, db=self.test_db, charset="utf8")
            cur_ = conn_.cursor()
            cur_.execute('select * from %s' % (self.test_temp_table))  
            data = cur_.fetchall()
            length = len(data)
            print('已挑选%s条测试音频'%(length))
            if length < int(self.test_loop_counter_limit):
                #os.system('PYTHONPATH=$PYTHONPATH:/home/user/linjr/online_label_api_dev/src  python /home/user/linjr/online_label_api_dev/src/local_api/data_prepare.py --DATA_TYPE 2')
                dp.prepare_data(prepare_type=2)
                time.sleep(float(self.time_sleep))
            else:
                break
        print('共挑选%s条测试音频'%(length))
        cur_.execute("update %s set data_uuid = '%s'" % (self.test_temp_table, uuid.uuid1()))
        conn_.commit()
        cur_.close()
        conn_.close()

        # passwd = self.cf.get('EngineServer', 'passwd')
        # os.system('echo %s|sudo -S chown -R admin:admin %s'%(passwd, os.path.abspath(os.path.join(os.getcwd(), \
        #           "../.."))))
        model_uuid_list, model_save_path_list, prepare_id_list = self.get_model()
        if len(model_uuid_list) == 0:
            generate_log.logger.debug('no new model has been generated!')
        else:
            generate_log.logger.debug('start testing new model!')
            test_data_uuid = self.cf.get('Uuid', 'test_data_uuid')
            # sftp = self.get_model_path()
            for i in range(len(model_uuid_list)):
                model_uuid, model_save_path, prepare_id = model_uuid_list[i], model_save_path_list[i], prepare_id_list[i]	
                # model_url = os.path.join(os.getcwd(), "..", model_save_path.split('/')[-1])
                # sftp.get(model_save_path, model_url)
                model_url = model_save_path
                os.system("sed -i -e 's#am_model=.*#am_model=%s#' -e 's#am_model_uuid=.*#am_model_uuid=%s#' \
                           -e 's#test_data_uuid=.*#test_data_uuid=%s#' %s" % (model_url, model_uuid, test_data_uuid, self.ini_path))
                self.run_test()
                # os.system("echo %s|sudo -S rm -r %s"%(passwd, model_url))

    def run_test(self):
        # =================
        # 1.Prepare Data
        # =================
        try:
            prepare_test_data.pre_data('config.ini').Copy_Wav()
            generate_log.logger.info("copy data to restful_path successful!")
        except Exception as exp:
            generate_log.logger.error("copy data to restful_path failed!")
            generate_log.logger.error(exp.message)

        # ================
        # 2.Replace Model
        # =================
        try:
            replace_model.rep_mol('config.ini').resetting()
            replace_model.rep_mol('config.ini').main()
            generate_log.logger.info("replace model successful!")
        except Exception as exp:
            generate_log.logger.error("replace model failed!")
            generate_log.logger.error(exp.message)

        # ================
        # 3.Modify Conf
        # =================
        try:
            modify_conf.modify_conf('config.ini').modify()
            generate_log.logger.info("modify conf successful!")
        except Exception as exp:
            generate_log.logger.error("modify conf failed!")
            generate_log.logger.error(exp.message)

        # ================
        # 4.For Engine
        # =================
        cwd_path = os.path.abspath(os.path.dirname(__file__))
        os.system('sh %s/../src/restart_engine.sh' %(cwd_path))

        # ==================
        # 5.For Test
        # ==================
        try:
            restfule_class.to_sql('config.ini')
            generate_log.logger.info("test successful!")
        except Exception as exp:
            generate_log.logger.error("test failed!")
            generate_log.logger.error(exp.message)

        # ==================
        # 6.Move Log
        # ==================
        try:
            move_log.move_log('config.ini')
            generate_log.logger.info("move log successful!")
        except Exception as exp:
            generate_log.logger.error("move log failed!")
            generate_log.logger.error(exp.message)

        # ==================
        # 7.Data_to_Mysql
        # ==================
        try:
            parse_log_to_mysql.access_log_to_mysql('config.ini').main()
            generate_log.logger.info("parse log to mysql successful!")
        except Exception as exp:
            generate_log.logger.error("parse log to mysql failed!")
            generate_log.logger.error(exp.message)
        try:
            calculate_to_mysql.write_data_to_sql('config.ini').main()
            generate_log.logger.info("calculate result to mysql successful!")
        except Exception as exp:
            generate_log.logger.error("calculate result to mysql failed!")
            generate_log.logger.error(exp.message)

        # ===================
        # 8.Generate Report
        # ===================
        try:
            report.Write_Report('config.ini').main()
            generate_log.logger.info("generate report successful!")
        except Exception as exp:
            generate_log.logger.error("generate report failed!")
            generate_log.logger.error(exp.message)

        # ===================
        # 9. Clear Pcm and Recover Model
        # ===================
        try:
            recover.rep_mol('config.ini').clear_pcm()
            generate_log.logger.info("clear pcm successful!")
        except Exception as exp:
            generate_log.logger.error("clear pcm failed!")
            generate_log.logger.error(exp.message)
        try:
            replace_model.rep_mol('config.ini').resetting()
            generate_log.logger.info("recover model successful!")
        except Exception as exp:
            generate_log.logger.error("recover model failed!")
            generate_log.logger.error(exp.message)


if __name__ == '__main__':
    cycle_test('config.ini').test()
