# -*- coding: utf-8 -*-
# =====================================================
# First, this file is used to copy data from remote server to local server.
# =====================================================
import sys
import generate_log
import os

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf-8')
import datetime
import paramiko
import pandas as pd
import shutil
from sqlalchemy import create_engine
from ConfigParser import ConfigParser
import httplib2


# ===================================

class pre_data():
    def __init__(self, ini_path):
        self.cwd_path = os.path.abspath(os.path.dirname(__file__))
        self.ini_path = os.path.join(self.cwd_path, '..', 'cfg', ini_path)
        self.cf = ConfigParser()
        self.cf.read(self.ini_path)
        self.restful_path = os.path.join(self.cf.get('Engine', 'Engine').split(':')[1],
                                         'service/data/servicedata/nls-filetrans')

    # Connecting Data Management Database
    def MySQL_Con(self):
        # Sql_host,Sql_port,Sql_user,Sql_passwd,Sql_database,Sql_table = parse_xml.sql_info(xml_path)
        Sql_host = self.cf.get('TestSQL', 'host')
        Sql_port = self.cf.get('TestSQL', 'port')
        Sql_user = self.cf.get('TestSQL', 'user')
        Sql_passwd = self.cf.get('TestSQL', 'passwd')
        Sql_database = self.cf.get('TestSQL', 'db')
        Sql_table = self.cf.get('TestSQL', 'temp_table')
        db_con = 'mysql+pymysql://' + Sql_user + ':' + Sql_passwd + '@' + Sql_host + ':' + Sql_port + '/' + Sql_database + '?charset=utf8'
        mysql_con = create_engine(db_con)
        audio_info = pd.read_sql('select * from ' + Sql_table, mysql_con)
        self.start_time = datetime.datetime.now() - datetime.timedelta(minutes=1)
        os.system("sed -i 's#start_time=.*#start_time=%s#' %s" % (self.start_time, self.ini_path))
        # sys.stdout = io.open('../logs/Data_extract_and_Generate_testfile.log','w+')
        # print('----------Start Time:' + self.start_time + '----------' + '\n')
        # print('Successful connection with database' + '\n')
        return audio_info

    # Establish a connection with the server of the data management database
    def Server_Con(self):
        ip = self.cf.get('RemoteServer', 'host')
        port = self.cf.get('RemoteServer', 'port')
        user = self.cf.get('RemoteServer', 'user')
        passwd = self.cf.get('RemoteServer', 'passwd')
        # ip,port,user,passwd = parse_xml.server_info(xml_path)
        remote_connection = paramiko.Transport((ip, int(port)))
        remote_connection.connect(username=user, password=passwd)
        sftp = paramiko.SFTPClient.from_transport(remote_connection)
        # print('Successful connection with server' + '\n')
        return sftp

    def Copy_Wav_(self):
        try:
            shutil.rmtree(self.restful_path)
        except:
            pass
        try:
            os.makedirs(self.restful_path)
        except:
            pass
        audio_info = self.MySQL_Con()
        sftp = self.Server_Con()
        for j in range(len(audio_info)):
            if audio_info['label_text'][j] is not None and audio_info['label_text'][j] != '':
                remote_file_path = '/home/admin/ng_tool_fs/audio_base' + audio_info['url'][j]
                # print(remote_file_path)
                wav_name = remote_file_path.split('/')[-1]
                sftp.get(remote_file_path, os.path.join(self.restful_path, wav_name))

    def Copy_Wav(self):
        try:
            shutil.rmtree(self.restful_path)
        except:
            pass
        try:
            os.makedirs(self.restful_path)
        except:
            pass
        audio_info = self.MySQL_Con()
        h = httplib2.Http()
        fs_host = self.cf.get('RemoteServer', 'host')
        fs_port = self.cf.get('RemoteServer', 'fs_port')
        for j in range(len(audio_info)):
            if audio_info['label_text'][j] is not None and audio_info['label_text'][j] != '':
                uttr_url = audio_info['url'][j]
                filename = uttr_url.split('/')[-1]
                wav_target_filepath = os.path.join(self.restful_path, filename)
                wav_target_filepath = os.path.abspath(wav_target_filepath)
                url = 'http://{}:{}{}'.format(fs_host, fs_port, uttr_url)
                # dp.logger.info(url)
                resp, content = h.request(url)
                if resp['status'] == '200':
                    with open(wav_target_filepath, 'wb') as f:
                        f.write(content)

 
if __name__ == '__main__':
    #try:
        pre_data('config.ini').Copy_Wav()
        generate_log.logger.info("copy data to restful_path successful!")
    #except Exception as exp:
        generate_log.logger.error("copy data to restful_path failed!")
        generate_log.logger.error(exp.message)

