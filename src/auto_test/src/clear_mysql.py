# -*- coding: utf-8 -*-
# =============================================
# This function is used to clear unuseful files
# =============================================
from ConfigParser import ConfigParser

import os
import pymysql


# ===================================


class clear_unuseful_files():
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
        self.temp_table = self.cf.get('TestSQL', 'temp_table')

    def Clear_files(self):
        conn = pymysql.Connect(user=self.user, password=self.passwd, port=int(self.port), host=self.host, db=self.db,
                               charset="utf8")
        cursor = conn.cursor()
        sql = "truncate %s" % self.temp_table
        cursor.execute(sql)
        cursor.close()
        conn.close()


if __name__ == '__main__':
    clear_unuseful_files('config.ini').Clear_files()
