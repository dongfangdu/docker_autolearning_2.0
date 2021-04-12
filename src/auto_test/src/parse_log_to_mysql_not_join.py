# -*- coding: utf-8 -*-
# =============================================
# This function is used to clear unuseful files
# =============================================
import io
import json
from ConfigParser import ConfigParser

import os
import pymysql


# ===================================


class access_log_to_mysql():
    def __init__(self, ini_path):
        self.cwd_path = os.path.abspath(os.path.dirname(__file__))
        self.ini_path = os.path.join(self.cwd_path, '..', 'cfg', ini_path)
        self.cf = ConfigParser()
        self.cf.read(self.ini_path)

    def parse_access_log(self):
        access_log_path = '../output/SaveLog/nls-cloud-asr/access.log'
        session_id, total_rtf, raw_rtf, real_rtf, duration, result = [], [], [], [], [], []
        access_file = io.open(access_log_path, encoding='utf-8').readlines()
        for line in access_file:
            line_dict = json.loads(line)
            session_id.append(line_dict['session_id'])
            total_rtf.append(line_dict['total_rtf'])
            raw_rtf.append(line_dict['raw_rtf'])
            real_rtf.append(line_dict['real_rtf'])
            duration.append(line_dict['duration'])
            result.append(line_dict['result'])
        return session_id, total_rtf, raw_rtf, real_rtf, duration, result

    def Update_mysql_table(self, session_id, total_rtf, raw_rtf, real_rtf, duration, result, conn):
        for i in range(len(session_id)):
            insert_content = 'total_rtf=' + total_rtf[i] + ',raw_rtf=' + raw_rtf[i] + ',real_rtf=' + real_rtf[
                i] + ',duration=' + duration[i] + ',par_log_text=' + '"' + result[i] + '"'
            sql_command = 'UPDATE asr_audio_info SET ' + insert_content + ' WHERE task_id=' + '"' + session_id[i] + '"'
            # print(sql_command)
            cursor = conn.cursor()
            cursor.execute(sql_command)
            conn.commit()
        conn.close()
        # print('Successed to parse access.log')

    def SQL_connect(self):
        host = self.cf.get('TestSQL', 'host')
        port = self.cf.get('TestSQL', 'port')
        user = self.cf.get('TestSQL', 'user')
        passwd = self.cf.get('TestSQL', 'passwd')
        db = self.cf.get('TestSQL', 'db')
        # print(user, passwd, int(port), host, db)
        conn = pymysql.Connect(user=user, password=passwd, port=int(port), host=host, db=db, charset="utf8")
        return conn

    def main(self):
        session_id, total_rtf, raw_rtf, real_rtf, duration, result = self.parse_access_log()
        conn = self.SQL_connect()
        self.Update_mysql_table(session_id, total_rtf, raw_rtf, real_rtf, duration, result, conn)


if __name__ == '__main__':
    try:
        access_log_to_mysql('config.ini').main()
        generate_log.logger.info("parse log to mysql successful!")
    except Exception as exp:
        generate_log.logger.error("parse log to mysql failed!")
        generate_log.logger.error(exp.message)
