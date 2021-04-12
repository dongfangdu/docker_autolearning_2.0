# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 10:40:32 2019

@author: 123
"""
from ConfigParser import ConfigParser
import generate_log
import os
import parse_log_to_mysql
import datetime
import replace_model


class rep_mol():
    def __init__(self, ini_path):
        self.cwd_path = os.path.abspath(os.path.dirname(__file__))
        self.ini_path = os.path.join(self.cwd_path, '..', 'cfg', ini_path)
        self.cf = ConfigParser()
        self.cf.read(self.ini_path)
        self.data_path = os.path.join(self.cf.get('Engine', 'Engine').split(':')[1],
                                      'service/data/servicedata/speech-alisr/data')

    def clear_pcm(self):
        req = parse_log_to_mysql.access_log_to_mysql('config.ini')
        req.parse_access_log()
        request_id = req.request_id
        dt = datetime.datetime.now()
        for id in request_id:
            year = dt.year
            month = dt.month
            day = dt.day
            pcm_path = os.path.join(self.data_path, str(year), str(month), str(day), 'default', id + '.pcm')
            if os.path.exists(pcm_path):
                os.remove(pcm_path)
            else:
                pass



if __name__ == '__main__':
    try:
        rep_mol('config.ini').clear_pcm()
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

