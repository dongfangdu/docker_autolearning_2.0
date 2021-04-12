# -*- coding:utf-8 -*-
import os


class Config:
    def __init__(self):
        pass

    DEBUG = True
    TESTING = False
    ENV = 'production'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'damnitintheworld, evilofthisproject'
    SQLALCHEMY_ECHO = False

    SQLALCHEMY_DATABASE_URI = 'mysql+cymysql://root:@192.168.108.197:3306/online_tagging_dev?charset=utf8'
    SQLALCHEMY_BINDS = {
        'al_web': 'mysql+cymysql://root:yjyjs123@192.168.106.170:3306/yj_autolearning_web?charset=utf8',
        'al_engine': 'mysql+cymysql://root:yjyjs123@192.168.106.170:3306/yj_autolearning_engine?charset=utf8',
        'al_train': 'mysql+cymysql://root:yjyjs123@192.168.106.170:3306/yj_autolearning_train?charset=utf8',
        'al_test': 'mysql+cymysql://root:yjyjs123@192.168.106.170:3306/yj_autolearning_test?charset=utf8',
        'al_label': 'mysql+cymysql://root:yjyjs123@192.168.106.170:3306/yj_autolearning_label?charset=utf8',
        'al_linjr': 'mysql+cymysql://root:@192.168.108.197:3306/linjr_test?charset=utf8',
    }

    UTTERANCE_FILE_SERVER = 'http://115.236.44.181:5000'

    LOGGING_CONFIG_PATH = './cfg/logging.yaml'
    LOGGING_PATH = './logs'

    DATA_SELECTION_TRAIN_DURATION_LIMIT = 7397000

    DATA_SELECTION_TRAIN_PREPARE_DIR = '/home/user/hezw/train_tmp_data'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True

    HOST = '127.0.0.1'
    PORT = 5000

    SQLALCHEMY_ECHO = True


config = {
    'development': DevelopmentConfig,
    'production': Config
}
