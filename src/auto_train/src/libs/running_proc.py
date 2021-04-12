# -*- coding: utf-8 -*-
import json
import os
import shutil
import sys
import traceback

import time
import xmltodict

from libs.common import get_config_dict, get_src_dir, get_project_dir, get_var_dir, current_timestamp_sec, get_uuid
from libs.enums import TrainModelStatusEnum
from libs.global_logger import get_logger
from libs.running_autotrain import RunningAutoTrain
from models.base_singleton import db
from models.train.train import TrainModelInfo, TrainRequestInfo

logger = get_logger(__name__)


# TODO 重复代码


def running_ds():
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
    RunningAutoTrain().execute('ds')
    cfg_dict = get_config_dict()

    data_selection_script = os.path.join(get_src_dir(), 'run_data_selection.py')
    command = '{} {} --train_uuid={}'.format(sys.executable, data_selection_script, train_uuid)
    logger.debug(command)

    import subprocess as sp
    child = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    streamdata = child.communicate()
    return_code = child.returncode
    if return_code != 0:
        print(streamdata[0])
        logger.error(streamdata[1])
        RunningAutoTrain().error(cur_proc_key)
        logger.info(u'{} 失败'.format(cur_proc_name))
        return False
    else:
        logger.info(streamdata[0])

    prepare_res_var_file = os.path.join(get_var_dir(), 'prepare_res_tmp.json')
    if not os.path.exists(prepare_res_var_file):
        logger.error(u'{} 结果文件丢失'.format(cur_proc_name))

    with open(prepare_res_var_file, mode='r') as f:
        prepare_res_tmp = str(f.read()).strip()
    prepare_res = json.loads(prepare_res_tmp)
    cur_prepare_res = prepare_res.get(train_uuid)
    if not cur_prepare_res and not cur_prepare_res.get('get'):
        logger.error(u'{} 结果丢失, train_uuid = {}'.format(cur_proc_name, train_uuid))
        RunningAutoTrain().error(cur_proc_key)
        return False

    prepare_uuid = cur_prepare_res['get'].get('prepare_uuid')
    prepare_data_path = cur_prepare_res['get'].get('prepare_data_path')
    prepare_status = cur_prepare_res['get'].get('prepare_status')

    if prepare_status != 1:
        logger.error(u'{} 数据伪准备好, prepare_uuid = {}'.format(cur_proc_name, prepare_uuid))
        RunningAutoTrain().error(cur_proc_key)
        return False

    # 入库
    session = db.db_session()
    train_req_info = session.query(TrainRequestInfo).filter(
        TrainRequestInfo.train_uuid == train_uuid,
        TrainRequestInfo.is_deleted == 0
    ).first()
    try:
        train_req_info.corpus_uuid = prepare_uuid
        train_req_info.corpus_dir = prepare_data_path
        session.commit()
        logger.info(u'模型对象入库，uuid: {}'.format(train_uuid))

    except Exception as e:
        session.rollback()
        session.close()
        logger.error(traceback.format_exc())
        logger.error(u'模型对象入库失败，{}'.format(e.message))
        RunningAutoTrain().error(cur_proc_key)
        logger.info(u'{} 失败'.format(cur_proc_name))
        return False

    RunningAutoTrain().finish(cur_proc_key)
    logger.info(u'{} 成功'.format(cur_proc_name))
    logger.info(u'{} -- 结束'.format(cur_proc_name))
    return True


def running_dp():
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

    # check ds res
    prepare_res_tmp = '{}'
    prepare_res_var_file = os.path.join(get_var_dir(), 'prepare_res_tmp.json')
    if os.path.exists(prepare_res_var_file) and os.path.isfile(prepare_res_var_file):
        with open(prepare_res_var_file, mode='r') as f:
            prepare_res_tmp = str(f.read()).strip()
    prepare_res = json.loads(prepare_res_tmp)
    if not prepare_res.get(train_uuid):
        logger.info(u'数据筛选未开始，得先执行ds')
        return False
    if not prepare_res[train_uuid].get('get') or \
            not prepare_res[train_uuid]['get'].get('prepare_data_path') or \
            prepare_res[train_uuid]['get']['prepare_data_path'] == '':
        logger.info(u'数据筛选未结束')
        return False
    if not prepare_res[train_uuid]['get']['prepare_status'] == 1:
        logger.info(u'数据筛选结束状态不正常')
        return False
    prepare_data_path = prepare_res[train_uuid]['get']['prepare_data_path']
    if not os.path.exists(prepare_data_path) or \
            not os.path.exists(os.path.join(prepare_data_path, 'txt')) or \
            not os.path.exists(os.path.join(prepare_data_path, 'wav')):
        logger.info(u'数据筛选存放路径有误')
        return False

    # setup parameters xml
    proc_full_name = 'data_parse'
    dp_xml_template = '{}_temp.xml'.format(proc_full_name)
    # train_module = 'am_training_pipeline'
    dp_xml_dir = os.path.join(get_project_dir(), 'bin', 'am_training_pipeline')
    with open(os.path.join(dp_xml_dir, dp_xml_template), mode='r') as f:
        dp_xml_dict = xmltodict.parse(f.read())

    oss_path_list = ['osstranscriptionpath', 'ossuploadrootpath', 'osswavpath', ]
    for oss_path in oss_path_list:
        real_path = dp_xml_dict['Recipe']['corpus']['@{}'.format(oss_path)]
        if real_path[0] != '/':
            real_path = os.path.abspath(os.path.join(prepare_data_path, real_path))
        dp_xml_dict['Recipe']['corpus']['@{}'.format(oss_path)] = real_path

    # save parameter to db # 入库
    # dp_xml_json = json.dumps(dp_xml_dict, indent=2)
    # print(dp_xml_json)  # TODO

    # save parameter to file # 生成配置文件
    dp_xml = xmltodict.unparse(dp_xml_dict, pretty=True)
    dp_xml_file = '{}_{}.xml'.format(proc_full_name, train_uuid)
    running_param_dir = os.path.join(get_project_dir(), 'cfg', 'running_param')
    if not os.path.exists(running_param_dir):
        os.makedirs(running_param_dir)

    with open(os.path.join(running_param_dir, dp_xml_file), mode='w') as f:
        f.write(dp_xml)
    time.sleep(1)

    # run script
    command_list = []
    running_var_dir = os.path.join(get_var_dir(), 'running_{}'.format(train_uuid))
    if not os.path.exists(running_var_dir):
        os.makedirs(running_var_dir)
    command_list.append('cd {}'.format(running_var_dir))

    train_tool_cfg = cfg_dict.get('TrainModelTool', None)
    command_list.append('{executable} {script} --inputxmlfilename {xml_file} --printlogcode > {log_file}'.format(
        executable=sys.executable,
        script=os.path.join(train_tool_cfg['pkg_path'], 'asrp.py'),
        xml_file=os.path.join(running_param_dir, dp_xml_file),
        log_file=os.path.join(running_var_dir, 'dp.log')
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


def running_dpf():
    cur_proc_key = str(sys._getframe().f_code.co_name).strip().split('_')[1]
    if not RunningAutoTrain.check_proc(cur_proc_key):
        logger.info(u'proc_key: {} 没有注册到到RunningTrain'.format(cur_proc_key))
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
    RunningAutoTrain().execute('dpf')
    cfg_dict = get_config_dict()
    custom_param_cfg = cfg_dict.get('CustomParam', {})

    running_var_dir = os.path.join(get_var_dir(), 'running_{}'.format(train_uuid))
    if not os.path.exists(running_var_dir):
        os.makedirs(running_var_dir)

    # check dp path
    dp_xml_file = '{}_{}.xml'.format('data_parse', train_uuid)
    running_param_dir = os.path.join(get_project_dir(), 'cfg', 'running_param')
    if not os.path.exists(running_param_dir) or \
            not os.path.exists(os.path.join(running_param_dir, dp_xml_file)):
        logger.info(u'数据解析(Data Parsing)运行配置不存在')
        return False
    with open(os.path.join(running_param_dir, dp_xml_file), mode='r') as f:
        dp_xml_dict = xmltodict.parse(f.read())
    if not dp_xml_dict.get('Recipe') or \
            not dp_xml_dict['Recipe'].get('corpus') or \
            not dp_xml_dict['Recipe']['corpus'].get('@ossuploadrootpath'):
        logger.info(u'数据解析(Data Parsing)配置不正确')
        return False
    dp_path = dp_xml_dict['Recipe']['corpus']['@ossuploadrootpath']
    if not os.path.exists(dp_path):
        logger.info(u'数据解析(Data Parsing)执行生成目录不存在')
        return False
    output_base_dir = os.path.abspath(os.path.join(dp_path, '../..'))

    # setup parameters xml
    proc_full_name = 'data_process_filter'
    dpf_xml_template = '{}_temp.xml'.format(proc_full_name)
    # train_module = 'am_training_pipeline'
    dpf_xml_dir = os.path.join(get_project_dir(), 'bin', 'am_training_pipeline')
    with open(os.path.join(dpf_xml_dir, dpf_xml_template), mode='r') as f:
        dpf_xml_dict = xmltodict.parse(f.read())

    output_dir = dpf_xml_dict['Recipe']['@outputDir']
    if output_dir[0] != '/':
        output_dir = os.path.abspath(os.path.join(output_base_dir, output_dir))
    dpf_xml_dict['Recipe']['@outputDir'] = output_dir

    resource_root_path = custom_param_cfg.get('resourceRootPath') or dpf_xml_dict['Recipe']['@resourceRootPath']
    if resource_root_path[0] != '/':
        resource_root_path = os.path.abspath(os.path.join(get_project_dir(), resource_root_path))
    if not os.path.exists(resource_root_path):
        logger.info(u'数据解析(Data Parsing): 参数 {} 不正确'.format('resourceRootPath'))
        return False
    dpf_xml_dict['Recipe']['@resourceRootPath'] = resource_root_path

    for rel_path in ['transcriptionList', 'waveList', ]:
        abs_path = dpf_xml_dict['Recipe']['EvaluateData']['Corpus']['@{}'.format(rel_path)]
        if abs_path[0] != '/':
            abs_path = os.path.abspath(os.path.join(dp_path, abs_path))
        dpf_xml_dict['Recipe']['EvaluateData']['Corpus']['@{}'.format(rel_path)] = abs_path

    # dpf_xml_json = json.dumps(dpf_xml_dict, indent=2)
    # print(dpf_xml_json)  # TODO

    # save parameter to file # 生成配置文件
    dpf_xml = xmltodict.unparse(dpf_xml_dict, pretty=True)
    dpf_xml_file = '{}_{}.xml'.format(proc_full_name, train_uuid)
    running_param_dir = os.path.join(get_project_dir(), 'cfg', 'running_param')
    if not os.path.exists(running_param_dir):
        os.makedirs(running_param_dir)

    with open(os.path.join(running_param_dir, dpf_xml_file), mode='w') as f:
        f.write(dpf_xml)
    time.sleep(1)

    # run script
    command_list = []
    command_list.append('cd {}'.format(running_var_dir))

    last_model_url = RunningAutoTrain().running_init_model_url
    if os.path.exists(last_model_url):
    	command_list.append('echo y|cp {} {}'.format(last_model_url,\
                            os.path.join(resource_root_path, '16k_general_wholeword', 'adv.model.ce.mdl')))
    	command_list.append('echo y|cp {} {}'.format(last_model_url,\
                            os.path.join(resource_root_path, '16k_general_wholeword_lfr', 'adv.model.ce.mdl')))

    train_tool_cfg = cfg_dict.get('TrainModelTool', None)
    command_list.append(
        '{executable} {script} --inputxmlfilename {xml_file} --printlogcode  --debug > {log_file}'.format(
            executable=sys.executable,
            script=os.path.join(train_tool_cfg['pkg_path'], 'asrp.py'),
            xml_file=os.path.join(running_param_dir, dpf_xml_file),
            log_file=os.path.join(running_var_dir, 'dpf.log')
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


def running_train():
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


def running_test():
    cur_proc_key = str(sys._getframe().f_code.co_name).strip().split('_')[1]
    if not RunningAutoTrain.check_proc(cur_proc_key):
        logger.info(u'proc_key: {} 没有注册到到RunningTrain'.format(cur_proc_key))
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

    running_var_dir = os.path.join(get_var_dir(), 'running_{}'.format(train_uuid))
    if not os.path.exists(running_var_dir):
        os.makedirs(running_var_dir)

    # run script
    command_list = []
    command_list.append('cd {}'.format(running_var_dir))

    command_list.append('echo testing > {log_file}'.format(
        log_file=os.path.join(running_var_dir, 'test.log')
    ))
    command = ' && '.join(command_list)
    logger.info(command)

    # import subprocess as sp
    # child = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    # streamdata = child.communicate()
    # return_code = child.returncode
    return_code = 0
    if return_code != 0:
        # logger.error(streamdata[1])
        RunningAutoTrain().error(cur_proc_key)
        logger.info(u'{} 失败'.format(cur_proc_name))
        return False
    else:
        # logger.info(streamdata[0])
        RunningAutoTrain().finish(cur_proc_key)
        logger.info(u'{} 成功'.format(cur_proc_name))

    logger.info(u'{} -- 结束'.format(cur_proc_name))
    return True


def running_sd():
    cur_proc_key = str(sys._getframe().f_code.co_name).strip().split('_')[1]
    if not RunningAutoTrain.check_proc(cur_proc_key):
        logger.info(u'proc_key: {} 没有注册到到RunningTrain'.format(cur_proc_key))
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
    # custom_param_cfg = cfg_dict.get('CustomParam', {})

    running_var_dir = os.path.join(get_var_dir(), 'running_{}'.format(train_uuid))
    if not os.path.exists(running_var_dir):
        os.makedirs(running_var_dir)

    # check dcs xml
    dcs_xml_file = '{}_{}.xml'.format('dcs_am_pipeline', train_uuid)
    running_param_dir = os.path.join(get_project_dir(), 'cfg', 'running_param')
    if not os.path.exists(running_param_dir) or \
            not os.path.exists(os.path.join(running_param_dir, dcs_xml_file)):
        logger.info(u'{}运行配置不存在'.format(RunningAutoTrain.get_proc_name('train')))
        return False
    with open(os.path.join(running_param_dir, dcs_xml_file), mode='r') as f:
        dcs_xml_dict = xmltodict.parse(f.read())

    if not dcs_xml_dict.get('Recipe') or \
            not dcs_xml_dict['Recipe'].get('@outputDir'):
        logger.info(u'{}配置不正确'.format(RunningAutoTrain.get_proc_name('train')))
        return False

    dcs_path = dcs_xml_dict['Recipe']['@outputDir']

    if not os.path.exists(dcs_path):
        logger.info(u'{}执行生成目录不存在'.format(RunningAutoTrain.get_proc_name('train')))
        return False

    model_dir = os.path.join(dcs_path, 'models')
    model_name = 'nnet_smbr'

    model_path = os.path.join(model_dir, model_name)
    print model_path
    if not os.path.exists(model_path):
        logger.info(u'{}模型文件丢失'.format(RunningAutoTrain.get_proc_name('train')))
        return False

    save_model_dir = os.path.join(get_var_dir(), 'models')
    if cfg_dict.get('SaveDataParam') and cfg_dict.get('SaveDataParam').get('save_model_dir'):
        save_model_dir = cfg_dict.get('SaveDataParam').get('save_model_dir')

    if not os.path.exists(save_model_dir):
        os.makedirs(save_model_dir)

    save_model_name = '{model_name}_{train_uuid}_{cur_timestamp}.net'
    if cfg_dict.get('SaveDataParam') and cfg_dict.get('SaveDataParam').get('save_model_name'):
        save_model_name = cfg_dict.get('SaveDataParam').get('save_model_name')
    print save_model_name
    cur_timestamp = current_timestamp_sec()
    smn_dict = {
        'model_name': model_name,
        'train_uuid': train_uuid,
        'cur_timestamp': cur_timestamp,
    }

    save_model_path = os.path.join(save_model_dir, save_model_name.format(**smn_dict))

    shutil.copy2(model_path, save_model_path)
    logger.info(u'{}：模型文件备份 {} --> {}'.format(cur_proc_name, model_path, save_model_path))

    model_uuid = get_uuid()
    # 写文件

    # 保存入库
    # if cfg_dict.get('RunShell') and \
    #         cfg_dict['RunShell'].get('is_save_db') and \
    #         cfg_dict['RunShell']['is_save_db'].lower() in ['t', 'on', 'true', 'yes', ]:
    logger.info(u'{}：入库'.format(cur_proc_name))
    session = db.db_session()

    model_info = TrainModelInfo()
    model_info.model_uuid = model_uuid
    model_info.model_url = save_model_path
    model_info.model_create_time = cur_timestamp
    model_info.model_status = TrainModelStatusEnum.READY.value
    model_info.train_uuid = train_uuid

    try:
        session.add(model_info)
        session.commit()
        logger.info(u'模型对象入库，uuid: {}'.format(train_uuid))

    except Exception as e:
        session.rollback()
        logger.error(traceback.format_exc())
        logger.error(u'模型对象入库失败，{}'.format(e.message))
        session.close()

        RunningAutoTrain().error(cur_proc_key)
        logger.info(u'{} 失败'.format(cur_proc_name))
        return False

    # RunningAutoTrain().finish(cur_proc_key)
    logger.info(u'{} 成功'.format(cur_proc_name))

    # RunningAutoTrain().finish_all()
    # logger.info(u'==========================================================')
    return True


def running_ctd():
    cur_proc_key = str(sys._getframe().f_code.co_name).strip().split('_')[1]
    if not RunningAutoTrain.check_proc(cur_proc_key):
        logger.info(u'proc_key: {} 没有注册到到RunningTrain'.format(cur_proc_key))
        return False

    cur_proc_name = RunningAutoTrain.get_proc_name(cur_proc_key)
    logger.info(u'{} -- 开始'.format(cur_proc_name))
    cfg_dict = get_config_dict()
    remove_param_cfg = cfg_dict.get('RemoveDataParam')
    path_list = remove_param_cfg['remove_data_path'].split(',')
    rm_day = remove_param_cfg['remove_day']
    if len(path_list) > 0:
        for mother_path in path_list:
            mother_path = mother_path.strip().rstrip("\n")
            son_list = os.listdir(mother_path)
            if len(son_list) > 0:
                for son_dir in son_list:
                    try:
                        filepath = os.path.join(mother_path, son_dir)
                        filetime = os.path.getctime(filepath)
                        time_record = time.localtime(filetime)
                        time_record = time.strftime("%Y-%m-%d %H:%M", time_record)
                        now_time = time.time()
                        time_diff = (now_time - filetime)/60/60/24
                        if time_diff >= int(rm_day):
                            shutil.rmtree(filepath, ignore_errors=True)
                    except Exception as e:
                        logger.error(traceback.format_exc())
                        logger.error(u'清空{}天前数据失败:{}'.format(rm_day, e.message))
        logger.info(u'清空{}天前数据成功'.format(rm_day))
    else:
        logger.info(u'数据清空列表为空')

    RunningAutoTrain().finish(cur_proc_key)

    logger.info(u'{} -- 结束'.format(cur_proc_name))
    return True


