# -*- coding: utf-8 -*-
import uuid
from ConfigParser import ConfigParser
import decimal
import datetime
import os
import pandas as pd
import pymysql
import numpy as np
import generate_log
from calculate import i_s_d_wer


class write_data_to_sql():
    def __init__(self, ini_path):
        self.cwd_path = os.path.abspath(os.path.dirname(__file__))
        self.ini_path = os.path.join(self.cwd_path, '..', 'cfg', ini_path)
        self.cf = ConfigParser()
        self.cf.read(self.ini_path)
        self.host = self.cf.get('TestSQL', 'host')
        self.port = self.cf.get('TestSQL', 'port')
        self.user = self.cf.get('TestSQL', 'user')
        self.passwd = self.cf.get('TestSQL', 'passwd')
        self.db = self.cf.get('TestSQL', 'db')
        self.test_temp_table = self.cf.get('TestSQL', 'temp_table')
        self.overall_table = self.cf.get('TestSQL', 'overall_table')
        self.sentence_table = self.cf.get('TestSQL', 'sentence_table')
        self.model_uuid = self.cf.get('Uuid', 'am_model_uuid')
        self.model_url = self.cf.get('Models', 'am_model')
        self.data_uuid = self.cf.get('Uuid', 'test_data_uuid')
        self.test_uuid = uuid.uuid1()
        self.start_time = self.cf.get('Time', 'start_time')

    def write_data_to_overall_test_results(self):
        conn = pymysql.Connect(user=self.user, password=self.passwd, port=int(self.port), host=self.host, db=self.db,
                               charset="utf8")
        cur = conn.cursor()
        cur.execute(
            'select task_id,request_id,path,url,label_text,res_text,par_log_text,total_rtf,raw_rtf,real_rtf,duration from %s where task_id is not null' % (
                self.test_temp_table))
        data = cur.fetchall()
        tables = pd.DataFrame(list(data),
                              columns=['task_id', 'request_id', 'path', 'url', 'label_text', 'res_text', 'par_log_text',
                                       'total_rtf', 'raw_rtf', 'real_rtf', 'duration'])
        all_tot_words = 0
        all_cor_words = 0
        all_ins_cnt = 0
        all_del_cnt = 0
        all_sub_cnt = 0
        all_err_sent_cnt = 0
        end_time = datetime.datetime.now() + datetime.timedelta(minutes=1)
        for i in range(len(tables)):
            table = tables.iloc[i]
            # print(table)
            task_id = table['task_id']
            request_id = table['request_id']
            path = table['path']
            url = table['url']
            label_text = table['label_text']
            res_text = table['res_text']
            par_log_text = table['par_log_text']
            total_rtf = table['total_rtf']
            raw_rtf = table['raw_rtf']
            real_rtf = table['real_rtf']
            duration = table['duration']
            if res_text == None:
                res_text = '~'
            if par_log_text == None:
                par_log_text = "~"
            if total_rtf == None:
                total_rtf = 0.000
            if raw_rtf == None:
                raw_rtf = 0.000
            if real_rtf == None:
                real_rtf = 0.000
            if duration == None or np.isnan(duration):
                duration =0
            tot_words, cor_words, word_cor_rate, word_err_rate, ins_cnt, del_cnt, sub_cnt = i_s_d_wer(label_text,res_text)
            temp_table_sql = "update %s set tot_words='%i', cor_words='%i', word_cor_rate='%f', word_err_rate='%f', ins_cnt='%i', del_cnt='%i', sub_cnt='%i', \
                              par_log_text='%s', total_rtf='%f', raw_rtf='%f', real_rtf='%f', duration='%i' where task_id='%s'" \
                             % (self.test_temp_table, int(tot_words), int(cor_words), word_cor_rate, word_err_rate, int(ins_cnt), \
                                int(del_cnt), int(sub_cnt), par_log_text, total_rtf, raw_rtf, real_rtf, duration, task_id)
            cur.execute(temp_table_sql)

            result_by_sentence_sql = "insert into %s (test_id, start_time, end_time, model_uuid, data_uuid, task_id, request_id, path, url, tot_words, cor_words, word_cor_rate,\
                                   word_err_rate, ins_cnt, del_cnt, sub_cnt, label_text, recog_text, par_log_text, total_rtf, raw_rtf, real_rtf, duration)\
                                   values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%i','%i','%f','%f','%i','%i','%i', '%s', '%s', '%s', '%f', '%f', '%f', '%i')" \
                                     % (self.sentence_table, self.test_uuid, self.start_time, end_time, self.model_uuid,\
                                        self.data_uuid, task_id, request_id, path, url, int(tot_words), \
                                        int(cor_words), word_cor_rate, word_err_rate, int(ins_cnt), int(del_cnt),\
                                        int(sub_cnt), label_text, res_text, par_log_text, total_rtf, raw_rtf, \
                                        real_rtf, duration)
            cur.execute(result_by_sentence_sql)
            all_tot_words += tot_words
            all_cor_words += cor_words
            all_ins_cnt += ins_cnt
            all_del_cnt += del_cnt
            all_sub_cnt += sub_cnt
            if tot_words != cor_words:
                all_err_sent_cnt += 1
        all_err_words = all_tot_words - all_cor_words
        all_word_err_rate = round(float(all_err_words) / (all_tot_words) * 100, 2)
        all_tot_sent_cnt = len(tables)
        all_sent_err_rate = round(float(all_err_sent_cnt) / (all_tot_sent_cnt) * 100, 2)
        overall_test_results_sql = "insert into %s (test_id, start_time, end_time, model_uuid, model_url, data_uuid, word_err_rate, tot_word_err_cnt, tot_word_cnt, ins_cnt, del_cnt, sub_cnt,\
				    sent_err_rate, err_sent_cnt, tot_sent_cnt) values ('%s','%s','%s','%s','%s','%s','%s','%i','%i','%i','%i','%i','%f','%i','%i')" % (
            self.overall_table, self.test_uuid, \
            self.start_time, end_time, self.model_uuid, self.model_url, self.data_uuid, all_word_err_rate,
            int(all_err_words), int(all_tot_words), int(all_ins_cnt), int(all_del_cnt), \
            int(all_sub_cnt), all_sent_err_rate, int(all_err_sent_cnt), int(all_tot_sent_cnt))
        cur.execute(overall_test_results_sql)
        cur.close()
        conn.commit()
        conn.close()

    def main(self):
        self.write_data_to_overall_test_results()


if __name__ == '__main__':
    try:
        write_data_to_sql('config.ini').main()
        generate_log.logger.info("calculate result to mysql successful!")
    except Exception as exp:
        generate_log.logger.error("calculate result to mysql failed!")
        generate_log.logger.error(exp.message)
