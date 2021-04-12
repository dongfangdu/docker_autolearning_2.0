# -*- coding:utf-8 -*-

from libs.global_logger import get_logger
from libs.running_autotrain import RunningAutoTrain
import os
from libs.common import get_var_dir
import shutil

logger = get_logger(__name__)


def main():
    # 获取训练参数和uuid
    logger.info(u'{} 执行自动训练程序'.format('*' * 10))

    print RunningAutoTrain().running_train_uuid

    print RunningAutoTrain.change_switch_mode('dp', 63, 'F')
    print RunningAutoTrain.get_status('dpf', 55)

    # RunningTrain().finish_all()


from libs import running_proc


def do_proc(proc_key):
    func_name = 'running_{}'.format(proc_key)
    if hasattr(running_proc, func_name):
        func = getattr(running_proc, func_name)
        func()
    else:
        logger.error(u'函数不存在：{}'.format(func_name))

def _main():
    try:
        os.system('rm -rf %s/running_*' %(get_var_dir()))
    except:
        pass
		
    train_uuid = RunningAutoTrain().running_train_uuid
    print train_uuid
 
    proc_key_list = ['ds', 'dp', 'dpf', 'train', 'test', 'sd', 'ctd']
    for proc_key in proc_key_list:
        do_proc(proc_key)
    '''
    proc_key_list = ['ds', 'dp', 'dpf', 'test', 'sd', 'ctd']
    for proc_key in proc_key_list:
        do_proc(proc_key)
        if proc_key == 'dpf':
            os.system("docker run --runtime=nvidia --net=host --name autolearning -v /home/user/linjr/:/home/user/linjr/ --rm nvidia/cuda2:latest /bin/bash -c 'python /home/user/linjr/auto_train/src/use_docker_train.py'")
    '''   
    RunningAutoTrain().finish_all()
    logger.info(u'==========================================================')

if __name__ == '__main__':
    _main()
    # while True:
    #     _main()
    #     continue
    # main()
    # train_uuid = RunningAutoTrain().running_train_uuid
    # print train_uuid
    #
    # proc_key_list = ['ds', 'dp', 'dpf', 'train', 'test', 'sd', ]
    # for proc_key in proc_key_list:
    #     do_proc(proc_key)
    # proc_key = 'dpf'
    # do_proc(proc_key)

    # is_clear = True
    # if is_clear:
    #     RunningAutoTrain().finish_all()
