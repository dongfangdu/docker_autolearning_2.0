# -*- coding: utf-8 -*-
import logging

import codecs
import os
import yaml
from flask import current_app

from app.libs.error_code import ResultSuccess
from app.libs.redprint import Redprint

api = Redprint('plugin')
logger = logging.getLogger(__name__)


@api.route('/list', methods=['GET'])
def plugin_list():
    for plugin in current_app.config['PLUGINS']:
        print plugin

    return ResultSuccess(msg='自学习插件列表', data=current_app.config.get('PLUGINS'))


@api.route('/update', methods=['GET'])
def plugin_update():
    plugins_cfg = current_app.config['PLUGINS_CONFIG_PATH']
    plugins_cfg = os.path.abspath(os.path.join(current_app.root_path, '{}'.format(plugins_cfg)))
    with codecs.open(plugins_cfg, 'r', encoding='utf-8') as f:
        plugins_cfg_dict = yaml.safe_load(f.read())
        # print plugins_cfg_dict['MODULES']

    current_app.config.update(plugins_cfg_dict)

    return ResultSuccess(msg='自学习插件列表', data=current_app.config.get('PLUGINS'))


@api.route('/show-cfg', methods=['GET'])
def plugin_show_config():
    pass


@api.route('/prep-label-once', methods=['GET'])
def plugin_prepare_label_data_once():
    pass


@api.route('/prep-train-once', methods=['GET'])
def plugin_prepare_train_data_once():
    pass


@api.route('/prep-test-once', methods=['GET'])
def plugin_prepare_test_data_once():
    pass


@api.route('/exec-train-once', methods=['POST'])
def plugin_execute_train_once():
    pass


@api.route('/exec-test-once', methods=['POST'])
def plugin_execute_test_once():
    pass


@api.route('/loop-train', methods=['GET'])
def plugin_loop_train_once():
    pass


@api.route('/loop-test', methods=['GET'])
def plugin_loop_test_once():
    pass
