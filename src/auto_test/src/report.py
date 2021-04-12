# -*- coding: utf-8 -*-
# This Scripts used to Report Each variables during the Test Procedure
# We choose Markdown as the presentation of reports
# The Report contents including
# 1. Distribution of Single Sentence WER
# 2. Distribution of Real Rtf
# 3. The Whole WER
# 4. Weigthen RTF
# 5. rtf --- WER(not finished, need write NEW-WER-CAL script)
# 6. duration --- WER(not finished, need write NEW-WER-CAL script)
# 7. Hardware Resource using(not finished temporarily)
# =======================================================
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import codecs
import matplotlib as mpl
import numpy as np
import os
import pandas as pd
import time
from sqlalchemy import create_engine

mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from ConfigParser import ConfigParser
import generate_log

# ===================================

class Write_Report():
    def __init__(self, ini_path):
        self.cwd_path = os.path.abspath(os.path.dirname(__file__))
        self.ini_path = os.path.join(self.cwd_path, '..', 'cfg', ini_path)
        self.cf = ConfigParser()
        self.cf.read(self.ini_path)
        self.output = os.path.join(self.cwd_path, '..', 'output', 'Report')
        self.engine = self.cf.get('Engine', 'Engine')
        self.model = self.cf.get('Models', 'am_model')
        self.time = time.strftime("%Y%m%d%H%M", time.localtime())
        self.out_path = os.path.join(self.output, self.time[:4], self.time[4:6], self.time[6:8], self.time)
        # print(self.time)
        try:
            os.makedirs(self.out_path)
        except:
            pass

    def _obtain_value(self):
        self.host = self.cf.get('TestSQL', 'host')
        self.port = self.cf.get('TestSQL', 'port')
        self.user = self.cf.get('TestSQL', 'user')
        self.passwd = self.cf.get('TestSQL', 'passwd')
        self.db = self.cf.get('TestSQL', 'db')
        self.temp_table = self.cf.get('TestSQL', 'temp_table')
        self.over_table = self.cf.get('TestSQL', 'overall_table')
        conn_str = 'mysql+pymysql://' + self.user + ':' + self.passwd + '@' + self.host + ':' + self.port + '/' + self.db + '?charset=utf8'
        engine = create_engine(conn_str)
        sql = "select duration,real_rtf,word_err_rate from %s where task_id is not null" % (self.temp_table)
        df = pd.read_sql_query(sql, engine)
        self.Weigthen_RTF = round(
            np.sum(np.array(df['real_rtf'].values, dtype=np.float32) * df['duration']) / np.sum(df['duration']), 2)
        self.Real_RTF = np.array(df['real_rtf'].values)
        self.single_WER = np.array(df['word_err_rate'].values)
        con_str = 'mysql+pymysql://' + self.user + ':' + self.passwd + '@' + self.host + ':' + self.port + '/' + self.db + '?charset=utf8'
        con_engine = create_engine(con_str)
        over_sql = "select word_err_rate,test_id,start_time,end_time from %s" % (self.over_table)
        df = pd.read_sql_query(over_sql, con_engine)
        self.whole_WER = str(np.array(df['word_err_rate'].values)[-1]) + '%'
        self.test_id = df['test_id'].values[-1]
        self.start_time = df['start_time'].values[-1]
        self.end_time = df['end_time'].values[-1]

    def _to_percent(self, temp, position):
        return '%.1f' % (temp / len(self.single_WER) * 100)

    def _to_percent_rtf(self, temp, position):
        return '%.1f' % (temp / len(self.Real_RTF) * 100)

    def _Distribution_WER(self):
        plt.style.use('ggplot')
        plt.hist(self.single_WER, 50, alpha=.7)
        plt.gca().yaxis.set_major_formatter(FuncFormatter(self._to_percent))
        plt.title("WER Distribution")
        plt.xlabel('Word  Error  Rate  of  Sentence(%)')
        plt.ylabel('Proportion  of  Total  Sentences(%)')
        plt.savefig(os.path.join(self.out_path, 'Wer_Distribution.png'))
        plt.close()

    def _Distribution_RTF(self):
        plt.style.use('ggplot')
        plt.hist(self.Real_RTF, 50, alpha=.7)
        plt.gca().yaxis.set_major_formatter(FuncFormatter(self._to_percent_rtf))
        plt.title('Real Rtf Distribution')
        plt.xlabel('Real  Time  Factor  of  Sentence')
        plt.ylabel('Proportion  of  Total  Sentences(%)')
        plt.savefig(os.path.join(self.out_path, 'Real_Rtf_Distribution.png'))
        plt.close()

    def _Write_func(self):
        f = codecs.open(os.path.join(self.out_path, 'Report.md'), 'w', encoding='utf-8')
        f.write(u'<center><font size=6>测 试 报 告</font></center>\n')
        f.write(u'>\t测试ID: %s\n' % (self.test_id))
        f.write(u'>\t开始时间: %s\n' % (str(self.start_time).split('.')[0].replace('T', ' ')))
        f.write(u'>\t结束时间: %s\n' % (str(self.end_time).split('.')[0].replace('T', ' ')))
        f.write(u'>\t测试引擎: %s\n' % self.engine)
        f.write(u'>\t测试模型: %s\n\n' % self.model)
        f.write(u'##1. 句错误率分布\n![wer_distribution](%s)\n\n' % ('./Wer_Distribution.png'))
        f.write(u'##2. 实时率分布\n![read_rtf_distribution](%s)\n\n' % ('./Real_Rtf_Distribution.png'))
        f.write(u'##3. 字错误率\n%s\n' % self.whole_WER)
        f.write(u'##4. rtf加权平均\n%s\n\n' % self.Weigthen_RTF)
        #print(u'字错误率: %s' % self.whole_WER)
        #print(u'rtf加权平均: %s' % self.Weigthen_RTF)
        f.close()
        ft = codecs.open(os.path.join(self.output, 'test_result.txt'), 'a+', encoding='utf-8')
        ft.write(u'>测试时间:%s   测试模型:%s   字错误率:%s' % (str(self.start_time).split('.')[0].replace('T', ' '), self.model, self.whole_WER) + '\n')
        ft.close()
		
    def main(self):
        self._obtain_value()
        self._Distribution_WER()
        self._Distribution_RTF()
        self._Write_func()


if __name__ == "__main__":
    #try:
        Write_Report('config.ini').main()
        generate_log.logger.info("generate report successful!")
    #except Exception as exp:
        generate_log.logger.error("generate report failed!")
        generate_log.logger.error(exp.message)

