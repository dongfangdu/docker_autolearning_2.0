# -*- coding:utf-8 -*-
import os
import sys

import argparse
import time

from libs.common import get_config_dict, get_package_path
from libs.global_logger import get_logger
from concurrent.futures import ProcessPoolExecutor

logger = get_logger(__name__)


def check_pkg_prepare_data_tool(venv_dir=None):
    if venv_dir:
        # venv_dir = "/home/user/hezw/work_py/venv/online_label_api"
        activate_script = os.path.join(venv_dir, "bin", "activate_this.py")
        execfile(activate_script, dict(__file__=activate_script))
    try:
        from local_api.data_prepare import DataPrepare
        return True
    except Exception as e:
        print e.message
        return False


def check_pkg_train_model_tool(venv_dir=None):
    if venv_dir:
        # venv_dir = "/home/user/hezw/work_py/venv/online_label_api"
        activate_script = os.path.join(venv_dir, "bin", "activate_this.py")
        execfile(activate_script, dict(__file__=activate_script))
    try:
        import argparse
        import asrpAction
        import asrpOSS
        import asrpGlobal
        return True
    except Exception as e:
        print e.message
        return False


def check_pkg():
    executor = ProcessPoolExecutor(max_workers=1)
    res = executor.submit(check_pkg_prepare_data_tool, '/home/user/linjr/venv/online_label_api').result()
    if not res:
        logger.error(u'数据筛选工具的环境测试失败')
        sys.exit(1)

    res = executor.submit(check_pkg_train_model_tool).result()
    if not res:
        logger.error(u'模型训练工具的环境测试失败')
        sys.exit(1)
    logger.info(u'所有工具依赖包的调用测试成功')


def setup_pth_file():
    site_package_path = get_package_path()
    if not site_package_path:
        logger.error(u'该项目虚拟环境sys.path有问题，缺乏site-packages路径')
        sys.exit(4)
    pth_file = os.path.join(site_package_path, 'auto_train_custom_pack.pth')
    logger.info(u'pth文件路径: {}'.format(pth_file))
    pth_list = []

    cfg_dict = get_config_dict()
    prepare_tool_cfg = cfg_dict.get('PrepareDataTool', None)
    if not prepare_tool_cfg:
        logger.error(u'数据筛选工具配置不存在，请在配置文件添加[PrepareDataTool]项')
        sys.exit(2)
    keys_verify = ['pkg_path', ]
    for key in keys_verify:
        if not prepare_tool_cfg.get(key):
            logger.error(u'数据筛选工具配置不正确，请在[PrepareDataTool]项添加 {}'.format(key))
            sys.exit(3)
    pth_list.append(prepare_tool_cfg['pkg_path'])

    train_tool_cfg = cfg_dict.get('TrainModelTool', None)
    if not train_tool_cfg:
        logger.error(u'训练工具配置不存在，请在配置文件添加[TrainModelTool]项')
        sys.exit(2)
    keys_verify = ['pkg_path', ]
    for key in keys_verify:
        if not train_tool_cfg.get(key):
            logger.error(u'训练工具配置不正确，请在[TrainModelTool]项添加 {}'.format(key))
            sys.exit(3)
    pth_list.append(train_tool_cfg['pkg_path'])
    with open(pth_file, 'w+') as f:
        f.writelines('{}\n'.format('\n'.join(pth_list)))
    logger.info(u'工具调用依赖路径配置成功')


if __name__ == '__main__':
    # setup_pth_file 和 check_pkg 不要在同一进程下执行
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', action="store", required=True, choices=['setup', 'check'],
                        help="input {setup,check}: setup用于设置pth文件; check用于检查pth配置是否正确")
    inputargs = parser.parse_args()

    # setup_pth_file()
    if inputargs.action == 'setup':
        setup_pth_file()
    elif inputargs.action == 'check':
        check_pkg()

