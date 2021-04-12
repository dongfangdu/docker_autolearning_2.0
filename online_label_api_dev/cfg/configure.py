# -*- coding:utf-8 -*-
import os

from .libs.builtin_extend import merge_dicts
from .models.db_utils import get_db_binds_dict
from .models.base import DB_V2_TABLE_PREFIX, DB_V2_SYSTEM_PREFIX
from ConfigParser import ConfigParser

class Config:
    def __init__(self):
        pass

    DEBUG = True
    TESTING = False
    ENV = 'default'

    cwd_path = os.path.abspath(os.path.dirname(__file__))
    ini_path = os.path.join(cwd_path, '../../..', 'auto_test/cfg', 'config.ini')
    cf = ConfigParser()
    cf.read(ini_path)

    FS_HOST = cf.get('RemoteServer', 'host')
    FS_PORT = cf.get('RemoteServer', 'fs_port')
	
    HOST = cf.get('EngineServer', 'host')
    PORT = cf.get('EngineServer', 'port')

    #FS_HOST = '192.168.106.170' #数据机IP
    #FS_PORT = 7779 #一般在外部署标注系统文件服务器（fs）的端口为7711, 7779为170数据库内部文件服务器端口

    #HOST = '192.168.100.210' #运行机IP
    #PORT = 1 #没用，不需要配置

    SECRET_KEY = 'damnitintheworld, evilofthisproject'

    # TOKEN 配置
    TOKEN_EXPIRATION = 2 * 24 * 3600  # 两天
    ADMIN_TOKEN_EXPIRATION = 3600  # 一小时

    # SQLALCHEMY配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_POOL_RECYCLE = 28800
    SQLALCHEMY_POOL_TIMEOUT = 28800
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_MAX_OVERFLOW = 100

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

    # 数据筛选开关
    LABEL_KEY = 'T'
    ENHAN_KEY = 'T'
    IDENT_KEY = 'T'

    # 数据筛选配置
    DATA_SELECTION_TRAIN_DURATION_LIMIT = 200000000 #时长限制（单位：毫秒）
    LABEL_LOOP_COUNTER_LIMIT = 300 #标注数据条数限制
    IDENT_LOOP_COUNTER_LIMIT = 1000 #识别数据条数限制
    TRAIN_LOOP_COUNTER_LIMIT = 2000 #训练数据条数据限制
    TIME_SLEEP = 300 #数据量不足时等待时长（单位：秒）
    DATA_SELECTION_TRAIN_PREPARE_DIR = '/home/user/linjr/train_tmp_data'

    SELECT_LABEL_LOOP_COUNTER_LIMIT = 100000 #挑去标注数据条数限制
    DATA_SELECTION_WEB_LABEL_DURATION_LIMIT = 200000000 #挑去标注时长限制（单位：毫秒）

    # 识别数据筛选阈值
    LABEL_THRESHOLD_PRE_WER = 20
    THRESHOLD_PRE_WER = 10
    THRESHOLD_LENGTH = 8

    # 其他独立模块配置
    PLUGINS_CONFIG_PATH = './plugins.yaml'

    # 运维管理配置
    # 下载
    DATA_DOWNLOAD_SV_TARGET_DIR = '/home/user/linjr/download_target'

    # 录音文件管理配置
    ASRC_SAVE_DIR = '/home/admin/online_label_data'

    # 语言模型配置
    LM_NGRAM_PATH = '/home/user/linjr/tools/big3_Smooth_5.lm'
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

