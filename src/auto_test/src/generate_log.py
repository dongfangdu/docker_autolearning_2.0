# coding=utf8
import logging
from logging import config
from ConfigParser import ConfigParser
import os

cwd_path = os.path.abspath(os.path.dirname(__file__))
ini_path = os.path.join(cwd_path, '..', 'cfg', 'config.ini')
cf = ConfigParser()
cf.read(ini_path)
log_dir = cf.get('SystemLog', 'saveSelfLogDir')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
    f = open(os.path.join(log_dir, 'Autotest.log'), 'w')
    f.close()
	
log_config = {
    "version": 1,
    'disable_existing_loggers': False,  # 是否禁用现有的记录器

    # 日志管理器集合
    'loggers': {
        # 管理器
        'Autotest_logger': {
            'handlers': ['console', 'log'],
            'level': 'DEBUG',
            'propagate': True,  # 是否传递给父记录器
        },
    },

    # 处理器集合
    'handlers': {
        # 输出到控制台
        'console': {
            'level': 'DEBUG',  # 输出信息的最低级别
            'class': 'logging.StreamHandler',
            'formatter': 'standard',  # 使用standard格式
            # 'filters': ['require_debug_true', ],  # 仅当 DEBUG = True 该处理器才生效
        },
        # 输出到文件
        'log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': '%s'%(os.path.join(log_dir, 'Autotest.log')),  # 输出位置
            'maxBytes': 1024 * 1024 * 100,  # 文件大小 100M
            'backupCount': 1,  # 备份份数
            'encoding': 'utf8',  # 文件编码
        },
    },

    # 日志格式集合
    'formatters': {
        # 标准输出格式
        'standard': {
            # [具体时间][日志名字:日志级别名称(日志级别ID)] [输出的模块:输出的函数]:日志内容
            'format': '[%(asctime)s] [%(name)s:%(levelname)-8s]--[%(module)s]:%(message)s'
            # 'format': '[%(asctime)s][%(name)s:%(levelname)s]--%(message)s'
        }
    }
}

config.dictConfig(log_config)
logger = logging.getLogger("Autotest_logger")
