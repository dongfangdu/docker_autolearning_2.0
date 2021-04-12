import codecs
from ConfigParser import ConfigParser
import os
import pymysql
import time
import generate_log
import datetime

class data_to_audio_table():
    def __init__(self, ini_path):
        self.cwd_path = os.path.abspath(os.path.dirname(__file__))
        self.ini_path = os.path.join(self.cwd_path, '..', 'cfg', ini_path)
        self.cf = ConfigParser()
        self.cf.read(self.ini_path)
        self.restful_path = os.path.join(self.cf.get('Engine', 'Engine').split(':')[1],
                                         'service/data/servicedata/nls-filetrans')
        self.audio_path = self.cf.get('Audio', 'audio_path')
        self.engine_passwd = self.cf.get('EngineServer', 'passwd')
        self.label_txt = self.cf.get('Audio', 'label_txt_path')
        self.test_data_uuid = self.cf.get('Uuid', 'test_data_uuid')

        self.host = self.cf.get('TestSQL', 'host')
        self.port = self.cf.get('TestSQL', 'port')
        self.user = self.cf.get('TestSQL', 'user')
        self.passwd = self.cf.get('TestSQL', 'passwd')
        self.db = self.cf.get('TestSQL', 'db')
        self.temp_table = self.cf.get('TestSQL', 'temp_table')
        self.overall_table = self.cf.get('TestSQL', 'overall_table')
        self.sentence_table = self.cf.get('TestSQL', 'sentence_table')
        self.start_time = datetime.datetime.now() 
        os.system("sed -i 's#start_time=.*#start_time=%s#' %s" % (self.start_time, self.ini_path))

    def copy_data(self):
        try:
            os.system('sh -c "ls %s/* | xargs -i rm -r {}"' % (self.restful_path))
        except:
            pass
        os.system('sh -c "ls %s/* | xargs -i cp -r {} %s"' % (self.audio_path, self.restful_path))
        # os.system('echo %s|sudo -S rm -r %s/*' %(self.engine_passwd, self.restful_path))
        # os.system('echo %s|sudo -S cp -r %s/* %s' %(self.engine_passwd, self.audio_path, self.restful_path))

    def audio_to_sql(self):
        conn = pymysql.Connect(user=self.user, password=self.passwd, port=int(self.port), host=self.host, db=self.db,
                               charset="utf8")
        cursor = conn.cursor()
        for wav_name in os.listdir(self.audio_path):
            _wav_name = wav_name.split('.')[0]
            sql = "insert into %s (request_id, data_uuid, path, url) values ('%s', '%s', '%s', '%s')" % (
                self.temp_table, _wav_name, self.test_data_uuid, self.audio_path, self.audio_path)
            cursor.execute(sql)
        cursor.close()
        conn.commit()
        conn.close()

    def label_to_sql(self):
        if self.label_txt != '':
            conn = pymysql.Connect(user=self.user, password=self.passwd, port=int(self.port), host=self.host,
                                   db=self.db, charset="utf8")
            cursor = conn.cursor()
            f = codecs.open('%s' % (self.label_txt), 'rb', encoding='utf-8-sig')
            for line in f.readlines():
                #print(line)
                wav_name   = line.split('	')[0].split('.')[0]
                label_text = line.split('	')[1]
                sql = "update %s set label_text='%s' where request_id='%s'" %(self.temp_table, label_text, wav_name)
                cursor.execute(sql)
            cursor.close()
            conn.commit()
            conn.close()
        else:
            pass

    def main(self):
        self.copy_data()
        self.audio_to_sql()
        time.sleep(1)
        self.label_to_sql()


if __name__ == '__main__':
    #try:
        data_to_audio_table('config.ini').main()
        generate_log.logger.info("test data prepare successful!")
    #except Exception as exp:
        generate_log.logger.error("test data prepare failed!")
        generate_log.logger.error(exp.message)

