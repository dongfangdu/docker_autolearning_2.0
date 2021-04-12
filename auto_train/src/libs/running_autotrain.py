# -*- coding: utf-8 -*-
import json
import os
import traceback

import shutil

from sqlalchemy import desc

from libs.common import get_uuid, get_config_dict, current_timestamp_sec, get_var_dir
from libs.global_logger import get_logger
from models.base_singleton import db
from models.train.train import TrainRequestInfo, TrainModelInfo, OverallResultInfo

logger = get_logger(__name__)


def get_last_model_url():
    last_model_url = get_config_dict().get('TrainModelTool', None)['last_model_url']
    #last_model_url = '/home/user/linjr/auto_train/corpus/model/fsmn.net.sc'
    # session = db.db_session()
    # model_info = session.query(TrainModelInfo).order_by(
    #     desc(TrainModelInfo.model_create_time)
    # ).first()
    session = db.db_session(bind='Test')
    model_info = session.query(OverallResultInfo).order_by(
        OverallResultInfo.word_err_rate
    ).first()
    if model_info:
        last_model_url = model_info.model_url
    session.close()
    return last_model_url


class RunningAutoTrain():

    __instance = None
    __request_info = None
    __id_file_name = 'running_train_id'
    __proc_mask = {
        'ds': ((1 << 2) - 1) ^ ((1 << 0) - 1),
        'dp': ((1 << 4) - 1) ^ ((1 << 2) - 1),
        'dpf': ((1 << 6) - 1) ^ ((1 << 4) - 1),
        'train': ((1 << 8) - 1) ^ ((1 << 6) - 1),
        'test': ((1 << 10) - 1) ^ ((1 << 8) - 1),
        'sd': ((1 << 12) - 1) ^ ((1 << 10) - 1),
        'ctd': ((1 << 14) - 1) ^ ((1 << 12) - 1),
    }
    __proc_name = {
        'ds': u'数据筛选(Data Selection)',
        'dp': u'数据解析(Data Parsing)',
        'dpf': u'数据过滤(Data Process Filter)',
        'train': u'模型训练(DNN Training)',
        'test': u'模型测试(DNN Test)',
        'sd': u'模型/解析数据入库(Save Model/Filter Data)',
        'ctd': u'清理过期数据(Clear Ovd Data)',
    }
    __mask_max_len = 14

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def gen_request_info(self):
        # TODO 对var中的running_train_id文件加 锁 和 权限 保护，免得被误删
        if not RunningAutoTrain.__request_info:
            session = db.db_session()
            train_uuid_var_file = os.path.join(get_var_dir(), RunningAutoTrain.__id_file_name)
            _train_uuid = None
            if os.path.exists(train_uuid_var_file) and os.path.isfile(train_uuid_var_file):
                with open(train_uuid_var_file, mode='r') as f:
                    _train_uuid = str(f.read()).strip()

            train_req_info = session.query(TrainRequestInfo).filter(
                TrainRequestInfo.train_uuid == _train_uuid,
                TrainRequestInfo.is_deleted == 0
            ).first()

            if not train_req_info:
                _train_uuid = get_uuid()
                switch_key_list = ['run_ds', 'run_dp', 'run_dpf', 'run_train', 'run_test', 'run_sd']
                run_shell_cfg = get_config_dict()['RunShell']
                train_switch_mode = 0
                for switch_key in switch_key_list:
                    proc_key = str(switch_key).replace('run_', '')
                    train_switch_mode = self.change_switch_mode(proc_key, train_switch_mode,
                                                                run_shell_cfg.get(switch_key))

                train_req_info = TrainRequestInfo()
                train_req_info.train_uuid = _train_uuid
                train_req_info.train_start_time = current_timestamp_sec()
                train_req_info.train_switch_mode = train_switch_mode
                train_req_info.train_status = 0
                train_req_info.init_model_url = get_last_model_url()

                try:
                    session.add(train_req_info)
                    session.commit()
                    logger.info(u'自动训练程序请求对象入库，uuid: {}'.format(_train_uuid))
                except Exception as e:
                    logger.error(traceback.format_exc())
                    logger.error(u'自动训练程序请求对象入库失败，{}'.format(e.message))
                    session.close()
                    raise RuntimeError(u'TrainRequestInfo创建失败')

            RunningAutoTrain.__request_info = dict(train_req_info)
            with open(train_uuid_var_file, mode='w+') as f:
                f.write(_train_uuid)
            session.close()
        return RunningAutoTrain.__request_info

    def finish_all(self):
        if RunningAutoTrain.__request_info:
            session = db.db_session()
            _train_uuid = RunningAutoTrain.__request_info['train_uuid']
            train_req_info = session.query(TrainRequestInfo).filter(
                TrainRequestInfo.train_uuid == _train_uuid,
                TrainRequestInfo.is_deleted == 0
            ).first()
            # TrainRequestInfo.train_status
            train_req_info.train_finish_time = current_timestamp_sec()
            session.commit()
            session.close()

        train_uuid_var_file = os.path.join(get_var_dir(), RunningAutoTrain.__id_file_name)
        if os.path.exists(train_uuid_var_file):
            os.remove(train_uuid_var_file)
        train_var_file = os.path.join(get_var_dir(), 'running_{}'.format(_train_uuid))
        if os.path.exists(train_var_file):
            shutil.rmtree(train_var_file)

        logger.info(u'自动训练全部执行完毕')

    def _inner_update_running_status(self, proc_key, status_flag):
        train_uuid = RunningAutoTrain().running_train_uuid
        train_state = RunningAutoTrain().running_train_status
        train_state = RunningAutoTrain.change_status_mode(proc_key, train_state, status_flag)

        session = db.db_session()
        train_req_info = session.query(TrainRequestInfo).filter(
            TrainRequestInfo.train_uuid == train_uuid,
            TrainRequestInfo.is_deleted == 0
        ).first()
        # TrainRequestInfo.train_status
        train_req_info.train_status = train_state
        session.commit()
        session.close()

    def execute(self, proc_key):
        self._inner_update_running_status(proc_key, 1)

    def error(self, proc_key):
        self._inner_update_running_status(proc_key, 2)

    def finish(self, proc_key):
        self._inner_update_running_status(proc_key, 3)

    @property
    def running_train_uuid(self):
        train_req_info = RunningAutoTrain().gen_request_info()
        return train_req_info['train_uuid']

    @property
    def running_train_switch_mode(self):
        train_req_info = RunningAutoTrain().gen_request_info()
        return train_req_info['train_switch_mode']

    @property
    def running_train_status(self):
        train_req_info = RunningAutoTrain().gen_request_info()
        return train_req_info['train_status']

    @property
    def running_train_verbose(self):
        train_req_info = RunningAutoTrain().gen_request_info()
        if train_req_info.get('train_verbose'):
            try:
                res = json.loads(train_req_info['train_verbose'])
            except Exception as e:
                res = {}
                logger.error(e.message)
                logger.error(traceback.format_exc())
            return res
        else:
            return {}

    @property
    def running_init_model_url(self):
        train_req_info = RunningAutoTrain().gen_request_info()
        return train_req_info['init_model_url']

    @staticmethod
    def change_switch_mode(proc_key, switch_mode, switch_flag):
        proc_mask = RunningAutoTrain.__proc_mask[proc_key]
        if not switch_flag:
            switch_flag = 'f'
        if isinstance(switch_flag, int):
            switch_flag = str(switch_flag)

        if switch_flag.lower() in ['t', 'on', 'true', 'yes', ]:
            return switch_mode | proc_mask
        else:
            return switch_mode & (~proc_mask)

    @staticmethod
    def is_switch_on(proc_key, switch_mode):
        return switch_mode & RunningAutoTrain.__proc_mask[proc_key] > 0

    @staticmethod
    def change_status_mode(proc_key, status_mode, status_flag):
        proc_mask = RunningAutoTrain.__proc_mask[proc_key]

        status_res = status_mode & (~proc_mask)
        status_flag = status_flag & 3  # TODO，现在每种proc占两个digit

        digit_counter = 0
        while True:
            if digit_counter >= RunningAutoTrain.__mask_max_len:
                break
            if (proc_mask & 1) > 0:
                break
            proc_mask = proc_mask >> 1
            status_flag = status_flag << 1
            digit_counter += 1
        return status_res | status_flag

    @staticmethod
    def get_status(proc_key, status_mode):
        proc_mask = RunningAutoTrain.__proc_mask[proc_key]

        status_res = status_mode & proc_mask
        digit_counter = 0
        while True:
            if digit_counter >= RunningAutoTrain.__mask_max_len:
                break
            if (proc_mask & 1) > 0:
                break
            proc_mask = proc_mask >> 1
            status_res = status_res >> 1
            digit_counter += 1
        return status_res

    @staticmethod
    def get_verbose(proc_key):
        train_verbose = RunningAutoTrain().running_train_verbose
        return train_verbose.get(proc_key)

    @staticmethod
    def get_proc_name(proc_key):
        return RunningAutoTrain.__proc_name.get(proc_key)

    @staticmethod
    def check_proc(proc_key):
        proc_name = RunningAutoTrain.__proc_name.get(proc_key)
        proc_mask = RunningAutoTrain.__proc_mask.get(proc_key)
        if not proc_name or not proc_mask:
            return False
        return True
