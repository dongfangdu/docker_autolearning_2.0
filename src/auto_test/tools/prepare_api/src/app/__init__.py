import codecs
import logging
import logging.config
import os

import yaml
from flask import Flask

from src.app.configure import config


def register_plugin(app):
    from .models.base import db
    db.init_app(app)



def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    if not os.path.exists(app.config['LOGGING_PATH']):
        os.mkdir(app.config['LOGGING_PATH'])

    logging_cfg = app.config['LOGGING_CONFIG_PATH']
    logging_cfg = os.path.abspath(os.path.join(app.root_path, '../../{}'.format(logging_cfg)))
    with codecs.open(logging_cfg, 'r', encoding='utf-8') as f:
        dict_conf = yaml.safe_load(f.read())
        # print dict_conf
    logging.config.dictConfig(dict_conf)

    register_plugin(app)

    return app
