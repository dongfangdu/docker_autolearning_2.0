# -*- coding:utf-8 -*-
import os

from .libs.builtin_extend import merge_dicts
from .models.db_utils import get_db_binds_dict
from .models.base import DB_V2_TABLE_PREFIX, DB_V2_SYSTEM_PREFIX


class Config:
    def __init__(self):
        pass

    DEBUG = True
    TESTING = False
    ENV = 'default'

    HOST = '192.168.108.197'
    PORT = 7810

    SECRET_KEY = 'damnitintheworld, evilofthisproject'

    # TOKEN 配置
    TOKEN_EXPIRATION = 2 * 24 * 3600  # 两天
    ADMIN_TOKEN_EXPIRATION = 1800  # 半小时

    # SQLALCHEMY配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_POOL_TIMEOUT = 20

    # SQLALCHEMY_DATABASE_URI = 'mysql+cymysql://root:@192.168.108.197:3306/online_tagging_dev?charset=utf8'
    SQLALCHEMY_DATABASE_URI = 'mysql+cymysql://root:yjyjs123@192.168.106.170:3306/online_tagging?charset=utf8'
    # 'mysql+cymysql://root:yjyjs123@192.168.106.170:3306/yj_autolearning_train?charset=utf8'
    SQLALCHEMY_BINDS = merge_dicts(get_db_binds_dict(), get_db_binds_dict('TRANSFER_SRC'))

    SQLALCHEMY_CUSTOM_SELECT_IN_STEP = 50

    # 分页配置
    DEFAULT_LISTNUM_PER_PAGE = 20
    TAGGING_PER_PAGE = 1

    # UTTERANCE_FILE_SERVER = 'http://115.236.44.181:5000'
    UTTERANCE_FILE_SERVER = 'http://192.168.106.170:7779'

    # 日志配置
    LOGGING_CONFIG_PATH = './logging.yaml'

    # 标注项目任务，编号生成配置
    BUSI_LBTASK_CODE_PREFIX = 'TTK'
    BUSI_LBTASK_CODE_PLACEHOLDER_NUM = 4

    BUSI_LBTASK_SV_CODE_PREFIX = 'OTK'
    BUSI_LBTASK_SV_CODE_PLACEHOLDER_NUM = 7

    BUSI_LBTASK_AUTO_SELECT_CODE_PREFIX = 'ATK'
    BUSI_LBTASK_AUTO_SELECT_CODE_PLACEHOLDER_NUM = 7

    BUSI_LBPROJECT_CODE_PREFIX = 'TPJ'
    BUSI_LBPROJECT_CODE_PLACEHOLDER_NUM = 3

    # 数据筛选配置
    DATA_SELECTION_TRAIN_DURATION_LIMIT = 7397000
    DATA_SELECTION_TRAIN_PREPARE_DIR = '/home/user/hezw/train_tmp_data'

    DATA_SELECTION_WEB_LABEL_DURATION_LIMIT = 2500000

    # 其他独立模块配置
    PLUGINS_CONFIG_PATH = './plugins.yaml'

    # 运维管理配置
    # 下载
    DATA_DOWNLOAD_SV_TARGET_DIR = '/home/user/hezw/download_target'

    # 录音文件管理配置
    ASRC_SAVE_DIR = '/home/admin/online_label_data'

    # 语言模型配置
    LM_NGRAM_PATH = '/home/user/xiaoqq/srilm_project/txt/big/big3_Smooth_5.lm'
    LM_NGRAM_ORDER = 4

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True

    HOST = '127.0.0.1'
    PORT = 5000

    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'mysql+cymysql://root:@192.168.108.197:3306/online_tagging?charset=utf8'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': Config
}
