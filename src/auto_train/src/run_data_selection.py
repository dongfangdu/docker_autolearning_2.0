# -*- coding: utf-8 -*-
import argparse
import os
import sys

import json

import time

from libs.common import get_config_dict, get_project_dir, get_var_dir
from libs.global_logger import get_logger
from setup_pkg import check_pkg_prepare_data_tool
sys.path.append('/home/user/linjr/online_label_api_dev/src')

logger = get_logger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--train_uuid', action="store", required=True, help="自动训练全局唯一ID")

    inputargs = parser.parse_args()

    cfg_dict = get_config_dict()
    prepare_tool_cfg = cfg_dict.get('PrepareDataTool', None)
    if not prepare_tool_cfg:
        logger.error(u'数据筛选工具配置不存在，请在配置文件添加[PrepareDataTool]项')
        sys.exit(1)

    '''
    venv_dir = prepare_tool_cfg.get('venv_path')
    if not check_pkg_prepare_data_tool(venv_dir):
        logger.error(u'数据筛选工具配置不正确，请检查venv_path，pkg_path是否正确')
        sys.exit(2)

    logger.info(u'接口调用参数 train_uuid={}'.format(inputargs.train_uuid))
    if venv_dir:
        activate_script = os.path.join(venv_dir, "bin", "activate_this.py")
        execfile(activate_script, dict(__file__=activate_script))
   '''

    from local_api.data_prepare import DataPrepare
    dp = DataPrepare()

    prepare_res_tmp = '{}'
    prepare_res_var_file = os.path.join(get_var_dir(), 'prepare_res_tmp.json')
    if os.path.exists(prepare_res_var_file) and os.path.isfile(prepare_res_var_file):
        with open(prepare_res_var_file, mode='r') as f:
            prepare_res_tmp = str(f.read()).strip()
    prepare_res = json.loads(prepare_res_tmp)

    cur_prepare_res = prepare_res.get(inputargs.train_uuid)
    print cur_prepare_res

    if not cur_prepare_res or not cur_prepare_res.get('post') or not cur_prepare_res['post'].get('prepare_uuid'):

        req_res = dp.prepare_data(prepare_type=1)
        res_dict = json.loads(req_res)
        print 'res_dict', res_dict
        prepare_uuid = res_dict['prepare_uuid']
        logger.info(u'数据准备全局唯一ID为 {}'.format(prepare_uuid))

        prepare_res_tmp = '{}'
        prepare_res_var_file = os.path.join(get_var_dir(), 'prepare_res_tmp.json')
        if os.path.exists(prepare_res_var_file) and os.path.isfile(prepare_res_var_file):
            with open(prepare_res_var_file, mode='r') as f:
                prepare_res_tmp = str(f.read()).strip()
        prepare_res = json.loads(prepare_res_tmp)
        cur_prepare_res = dict(post=res_dict)
        prepare_res[inputargs.train_uuid] = cur_prepare_res

        with open(prepare_res_var_file, mode='w') as f:
            f.write(json.dumps(prepare_res, indent=2))
        logger.debug(json.dumps(prepare_res, indent=2))

        time.sleep(1)

    prepare_uuid = cur_prepare_res['post']['prepare_uuid']
    cur_res = cur_prepare_res.get('get')
    loop_counter = 0
    loop_counter_limit = cfg_dict.get('PrepareDataTool')['loop_counter_limit'] or 60
    loop_sleep = cfg_dict.get('PrepareDataTool')['loop_sleep'] or 60
    while True:
        if loop_counter > loop_counter_limit:
            logger.error(u'已超出轮询次数，当前接口状态为{}'.format(cur_res.get('prepare_status')))
            break
        if cur_res and cur_res.get('prepare_status') == 1:
            break
        cur_res = json.loads(dp.is_ready(prepare_uuid))
        time.sleep(float(loop_sleep))
        loop_counter = loop_counter + 1
        # logger.info(time.time())

    cur_prepare_res['get'] = cur_res
    prepare_res[inputargs.train_uuid] = cur_prepare_res

    with open(prepare_res_var_file, mode='w') as f:
        f.write(json.dumps(prepare_res, indent=2))
    logger.debug(json.dumps(prepare_res, indent=2))

    if not cur_res.get('prepare_status') == 1:
        sys.exit(1)


