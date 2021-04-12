# -*- coding: utf-8 -*-
import json
import os
import shutil
import sys
import traceback

import time
# while True:
#     returncode = os.system("yum -y install epel-release pip")
#     if returncode == 0:
#         break
#     else:
#         continue
# os.system("curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python get-pip.py")
os.system("pip install -i https://pypi.tuna.tsinghua.edu.cn/simple xmltodict==0.12.0 PyYAML==5.1.1 SQLAlchemy==1.3.3 cymysql==0.9.13")
import xmltodict

from libs.common import get_config_dict, get_src_dir, get_project_dir, get_var_dir, current_timestamp_sec, get_uuid
# from libs.enums import TrainModelStatusEnum
from libs.global_logger import get_logger
from libs.running_autotrain import RunningAutoTrain
from models.base_singleton import db
from models.train.train import TrainModelInfo, TrainRequestInfo

logger = get_logger(__name__)

def running_train():
    # os.system("docker run -it --runtime=nvidia --net=host -v /home/user/linjr/:/home/user/linjr/ --rm nvidia/cuda:8.0-runtime-centos7 bash")
    os.system("yum -y install pciutils perl")

    cur_proc_key = str(sys._getframe().f_code.co_name).strip().split('_')[1]
    if not RunningAutoTrain.check_proc(cur_proc_key):
        logger.info(u'proc_key: {} 没有注册到到RunningTrain')
        return False
    cur_proc_name = RunningAutoTrain.get_proc_name(cur_proc_key)

    logger.info(u'{} -- 开始'.format(cur_proc_name))
    train_uuid = RunningAutoTrain().running_train_uuid
    train_switch_mode = RunningAutoTrain().running_train_switch_mode
    logger.info(u'当前运行自动训练id: {}'.format(train_uuid))
    if not RunningAutoTrain.is_switch_on(cur_proc_key, train_switch_mode):
        logger.info(u'{} 开关关闭'.format(cur_proc_name))
        return False

    # common variable
    RunningAutoTrain().execute(cur_proc_key)
    cfg_dict = get_config_dict()
    custom_param_cfg = cfg_dict.get('CustomParam', {})

    running_var_dir = os.path.join(get_var_dir(), 'running_{}'.format(train_uuid))
    if not os.path.exists(running_var_dir):
        os.makedirs(running_var_dir)

    # check dpf xml
    dpf_xml_file = '{}_{}.xml'.format('data_process_filter', train_uuid)
    running_param_dir = os.path.join(get_project_dir(), 'cfg', 'running_param')
    if not os.path.exists(running_param_dir) or \
            not os.path.exists(os.path.join(running_param_dir, dpf_xml_file)):
        logger.info(u'数据过滤(Data Process Filter)运行配置不存在')
        return False
    with open(os.path.join(running_param_dir, dpf_xml_file), mode='r') as f:
        dpf_xml_dict = xmltodict.parse(f.read())
    if not dpf_xml_dict.get('Recipe') or \
            not dpf_xml_dict['Recipe'].get('@outputDir'):
        logger.info(u'数据过滤(Data Process Filter)配置不正确')
        return False
    dpf_path = dpf_xml_dict['Recipe']['@outputDir']
    if not os.path.exists(dpf_path):
        logger.info(u'数据过滤(Data Process Filter)执行生成目录不存在')
        return False
    output_base_dir = os.path.abspath(os.path.join(dpf_path, '../..'))

    ######################
    # setup parameters xml
    proc_full_name = 'dcs_am_pipeline'
    dcs_xml_template = '{}_temp.xml'.format(proc_full_name)
    # train_module = 'am_training_pipeline'
    dcs_xml_dir = os.path.join(get_project_dir(), 'bin', 'am_training_pipeline')
    with open(os.path.join(dcs_xml_dir, dcs_xml_template), mode='r') as f:
        dcs_xml_dict = xmltodict.parse(f.read())

    # @outputDir
    output_dir = dcs_xml_dict['Recipe']['@outputDir']
    if output_dir[0] != '/':
        output_dir = os.path.abspath(os.path.join(output_base_dir, output_dir))
    dcs_xml_dict['Recipe']['@outputDir'] = output_dir

    # @resourceRootPath
    resource_root_path = custom_param_cfg.get('resourceRootPath') or dcs_xml_dict['Recipe']['@resourceRootPath']
    if resource_root_path[0] != '/':
        resource_root_path = os.path.abspath(os.path.join(get_project_dir(), resource_root_path))
    if not os.path.exists(resource_root_path):
        logger.info(u'模型训练(DNN Training): 参数 {} 不正确'.format('resourceRootPath'))
        return False
    dcs_xml_dict['Recipe']['@resourceRootPath'] = resource_root_path

    # CorpusList/Corpus/@SmbrTrainFeatureLabelPath
    smbr_train_feature_label_path = dcs_xml_dict['Recipe']['CorpusList']['Corpus']['@SmbrTrainFeatureLabelPath']
    if smbr_train_feature_label_path[0] != '/':
        smbr_train_feature_label_path = os.path.abspath(os.path.join(running_var_dir, smbr_train_feature_label_path))
    dcs_xml_dict['Recipe']['CorpusList']['Corpus']['@SmbrTrainFeatureLabelPath'] = smbr_train_feature_label_path

    # SmbrTrain/@featureTrans
    feature_trans = dcs_xml_dict['Recipe']['SmbrTrain']['@featureTrans']
    if feature_trans[0] != '/':
        feature_trans = os.path.abspath(os.path.join(get_project_dir(), feature_trans))
    dcs_xml_dict['Recipe']['SmbrTrain']['@featureTrans'] = feature_trans

    # SmbrTrain/@initModel
    init_model = dcs_xml_dict['Recipe']['SmbrTrain']['@initModel']
    if custom_param_cfg.get('init_model_type') == 'iter':
        last_model_url = RunningAutoTrain().running_init_model_url
        if last_model_url[0] != '/':
            last_model_url = os.path.abspath(os.path.join(get_project_dir(), last_model_url))
        if os.path.exists(last_model_url):
            init_model = last_model_url
    if init_model[0] != '/':
        init_model = os.path.abspath(os.path.join(get_project_dir(), init_model))
    dcs_xml_dict['Recipe']['SmbrTrain']['@initModel'] = init_model

    ######################

    # dcs_xml_json = json.dumps(dcs_xml_dict, indent=2)
    # print(dcs_xml_json)  # TODO

    # save parameter to file # 生成配置文件
    dcs_xml = xmltodict.unparse(dcs_xml_dict, pretty=True)
    dcs_xml_file = '{}_{}.xml'.format(proc_full_name, train_uuid)
    running_param_dir = os.path.join(get_project_dir(), 'cfg', 'running_param')
    if not os.path.exists(running_param_dir):
        os.makedirs(running_param_dir)

    with open(os.path.join(running_param_dir, dcs_xml_file), mode='w') as f:
        f.write(dcs_xml)
    time.sleep(1)

    # run script
    command_list = []
    command_list.append('cd {}'.format(running_var_dir))

    train_tool_cfg = cfg_dict.get('TrainModelTool', None)  # TODO
    command_list.append(
        '{executable} {script} --inputxmlfilename {xml_file} --printlogcode  --debug > {log_file}'.format(
            executable=sys.executable,
            script=os.path.join(train_tool_cfg['pkg_path'], 'asrp.py'),
            xml_file=os.path.join(running_param_dir, dcs_xml_file),
            log_file=os.path.join(running_var_dir, 'dcs.log')
        ))
    command = ' && '.join(command_list)
    logger.info(command)

    import subprocess as sp
    child = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    streamdata = child.communicate()
    return_code = child.returncode
    # return_code = 0
    if return_code != 0:
        logger.error(streamdata[1])
        RunningAutoTrain().error(cur_proc_key)
        logger.info(u'{} 失败'.format(cur_proc_name))
        return False
    else:
        logger.info(streamdata[0])
        RunningAutoTrain().finish(cur_proc_key)
        logger.info(u'{} 成功'.format(cur_proc_name))

    logger.info(u'{} -- 结束'.format(cur_proc_name))
    return True


if __name__ == '__main__':
    running_train()