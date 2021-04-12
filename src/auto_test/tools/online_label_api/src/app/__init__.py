# -*- coding: utf-8 -*-

import logging
import logging.config

import codecs
import os
import yaml
from flask_cors import CORS
from flask_socketio import SocketIO

from .app import Flask
from .configure import config
from .libs import path_utils


def register_blueprints(app):
    from .api.v1 import create_blueprint_v1
    from .api.v2 import create_blueprint_v2
    from .api.vX import create_blueprint_vX
    from .api.sysmng import create_blueprint_sysmng
    from .api.sysmgr import create_blueprint_sysmgr
    app.register_blueprint(create_blueprint_v1(), url_prefix='/api/v1')
    app.register_blueprint(create_blueprint_v2(), url_prefix='/api/v2')
    app.register_blueprint(create_blueprint_vX(), url_prefix='/api/vX')
    app.register_blueprint(create_blueprint_sysmng(), url_prefix='/api/')
    app.register_blueprint(create_blueprint_sysmgr(), url_prefix='/api/v2')


def register_plugin(app):
    from .models.base import db_v1, db_v2
    db_v1.init_app(app)
    db_v2.init_app(app)

    # 语言模型的初始化
    from .libs.lm_tool.lm_utils import LMv1
    lm_v1 = LMv1()
    lm_v1.init_app(app)
    # db_v2.check_db_connections(app=app)

    # with app.app_context():
    #     db.create_all()

    # 跨域处理
    CORS(app, supports_credentials=True)
    # socketio.init_app(app=app, async_mode=None)

    from .models.base import asynchronous_executor, transfer_executor
    asynchronous_executor.init_app(app)
    transfer_executor.init_app(app)


def create_app(config_name, update_cfg=None, logging_cfg=None, plugins_cfg=None):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # custom config

    # logging config
    # logging_cfg_arg = logging_cfg
    if logging_cfg:
        if logging_cfg[0] != '/':
            logging_cfg = os.path.abspath(os.path.join(path_utils.get_project_dir(), logging_cfg))
    if not logging_cfg or not os.path.exists(logging_cfg):
        # raise IOError(u'日志配置文件不存在：{}'.format(logging_cfg_arg))
        logging_cfg = app.config['LOGGING_CONFIG_PATH']
        logging_cfg = os.path.abspath(os.path.join(app.root_path, '{}'.format(logging_cfg)))
    with codecs.open(logging_cfg, 'r', encoding='utf-8') as f:
        logging_cfg_dict = yaml.safe_load(f.read())
        handlers = logging_cfg_dict.get('handlers')
        if handlers:
            for handle_k, handler in handlers.items():
                if not handler.get('filename'):
                    continue
                log_filename = os.path.basename(handler['filename'])
                log_dir = os.path.dirname(handler['filename'])
                if log_dir[0] != '/':
                    log_dir = os.path.join(path_utils.get_project_dir(), log_dir)
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                logging_cfg_dict['handlers'][handle_k]['filename'] = os.path.join(log_dir, log_filename)
        # print logging_cfg_dict
    logging.config.dictConfig(logging_cfg_dict)

    # custom plugin config
    if plugins_cfg:
        if plugins_cfg[0] != '/':
            plugins_cfg = os.path.abspath(os.path.join(path_utils.get_project_dir(), plugins_cfg))
    if not plugins_cfg or not os.path.exists(plugins_cfg):
        plugins_cfg = app.config['PLUGINS_CONFIG_PATH']
        plugins_cfg = os.path.abspath(os.path.join(app.root_path, '{}'.format(plugins_cfg)))
    with codecs.open(plugins_cfg, 'r', encoding='utf-8') as f:
        plugins_cfg_dict = yaml.safe_load(f.read())

    plugins_cfg = app.config['PLUGINS_CONFIG_PATH']
    plugins_cfg = os.path.abspath(os.path.join(app.root_path, '{}'.format(plugins_cfg)))
    with codecs.open(plugins_cfg, 'r', encoding='utf-8') as f:
        plugins_cfg_dict = yaml.safe_load(f.read())

    app.config.update(plugins_cfg_dict)

    register_blueprints(app)
    register_plugin(app)

    return app


socketio = SocketIO()
