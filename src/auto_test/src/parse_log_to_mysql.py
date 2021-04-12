# -*- coding: utf-8 -*-
# =============================================
# This function is used to clear unuseful files
# =============================================
import io
import json
from ConfigParser import ConfigParser

import os
import pymysql

import generate_log


# ===================================


class access_log_to_mysql():
    def __init__(self, ini_path):
        self.cwd_path = os.path.abspath(os.path.dirname(__file__))
        self.ini_path = os.path.join(self.cwd_path, '..', 'cfg', ini_path)
        self.cf = ConfigParser()
        self.cf.read(self.ini_path)

    def parse_access_log(self):
        access_log_path = os.path.join(self.cf.get('Output', 'output_path'), 'SaveLog/nls-cloud-asr/access.log')
        passwd = self.cf.get('EngineServer', 'passwd')
        #os.system('echo %s|sudo -S chmod -R 777 %s'%(passwd, access_log_path))
        #os.system('echo %s|sudo -S chown -R admin:admin %s'%(passwd, access_log_path))
        session_id, total_rtf, raw_rtf, real_rtf, duration, result, self.request_id = [], [], [], [], [], [], []
        # session_id,total_rtf,raw_rtf,real_rtf,duration,result = [],[],[],[],[],[]
        access_file = io.open(access_log_path, encoding='utf-8').readlines()
        session_id_set, repeat_session_id_content = set(), {}
        for line in access_file:
            line_dict = json.loads(line)
            if line_dict['session_id'] in session_id:
                session_id_set.add(line_dict['session_id'])
                if line_dict['session_id'] not in repeat_session_id_content:
                    repeat_session_id_content[line_dict['session_id']] = []
                process_values = [session_id.index(line_dict['session_id']), float(line_dict['total_rtf']),
                                  float(line_dict['raw_rtf']),
                                  float(line_dict['real_rtf']), int(line_dict['duration']), line_dict['result']]
                repeat_session_id_content[line_dict['session_id']].append(process_values)
                self.request_id.append(line_dict['request_id'])
            else:
                self.request_id.append(line_dict['request_id'])
                session_id.append(line_dict['session_id'])
                total_rtf.append(line_dict['total_rtf'])
                raw_rtf.append(line_dict['raw_rtf'])
                real_rtf.append(line_dict['real_rtf'])
                duration.append(line_dict['duration'])
                result.append(line_dict['result'])
        for element in session_id_set:
            for j in range(len(repeat_session_id_content[element])):
                index = repeat_session_id_content[element][0][0]
                if j == 0:
                    total_rtf[index] = float(total_rtf[index]) * int(duration[index]) + \
                                       repeat_session_id_content[element][j][1] * repeat_session_id_content[element][j][
                                           4]
                    raw_rtf[index] = float(raw_rtf[index]) * int(duration[index]) + \
                                     repeat_session_id_content[element][j][2] * repeat_session_id_content[element][j][4]
                    real_rtf[index] = float(real_rtf[index]) * int(duration[index]) + \
                                      repeat_session_id_content[element][j][3] * repeat_session_id_content[element][j][
                                          4]
                    duration[index] = int(duration[index]) + repeat_session_id_content[element][j][4]
                else:
                    total_rtf[index] += repeat_session_id_content[element][j][1] * \
                                        repeat_session_id_content[element][j][4]
                    raw_rtf[index] += repeat_session_id_content[element][j][2] * repeat_session_id_content[element][j][
                        4]
                    real_rtf[index] += repeat_session_id_content[element][j][3] * repeat_session_id_content[element][j][
                        4]
                    duration[index] += repeat_session_id_content[element][j][4]
                result[index] += '' + repeat_session_id_content[element][j][5]
            total_rtf[index] = str('%.3f' % (total_rtf[index] / duration[index]))
            raw_rtf[index] = str('%.3f' % (raw_rtf[index] / duration[index]))
            real_rtf[index] = str('%.3f' % (real_rtf[index] / duration[index]))
            duration[index] = duration[index] / len(repeat_session_id_content[element])
        return session_id, total_rtf, raw_rtf, real_rtf, duration, result

    def Update_mysql_table(self, table, session_id, total_rtf, raw_rtf, real_rtf, duration, result, conn):
        for i in range(len(session_id)):
            insert_content = 'total_rtf=' + total_rtf[i] + ',raw_rtf=' + raw_rtf[i] + ',real_rtf=' + real_rtf[
                i] + ',duration=' + str(duration[i]) + ',par_log_text=' + '"' + result[i] + '"'
            sql_command = 'UPDATE %s SET ' % (table) + insert_content + ' WHERE task_id=' + '"' + session_id[i] + '"'
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
        self.table = self.cf.get('TestSQL', 'temp_table')
        # print(user, passwd, int(port), host, db)
        conn = pymysql.Connect(user=user, password=passwd, port=int(port), host=host, db=db, charset="utf8")
        return conn

    def main(self):
        session_id, total_rtf, raw_rtf, real_rtf, duration, result = self.parse_access_log()
        conn = self.SQL_connect()
        self.Update_mysql_table(self.table, session_id, total_rtf, raw_rtf, real_rtf, duration, result, conn)


if __name__ == '__main__':
    #try:
        access_log_to_mysql('config.ini').main()
        generate_log.logger.info("parse log to mysql successful!")
    #except Exception as exp:
        generate_log.logger.error("parse log to mysql failed!")
        generate_log.logger.error(exp.message)
