# -*- coding: utf-8 -*-
import csv
import os
import hashlib
import codecs
import zipfile
import logging
import yaml
import sys
reload(sys)
sys.setdefaultencoding('utf8')
logger = logging.getLogger(__name__)


def generate_file_md5(rootdir, filename, blocksize=2 ** 20):
    m = hashlib.md5()
    with open(os.path.join(rootdir, filename), "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest()


def read_yaml(config_name, config_path):
    if config_name and config_path:
        with codecs.open(config_path, 'r', encoding='utf-8') as f:
            conf = yaml.safe_load(f.read())
        if config_name in conf.keys():
            return conf[config_name.upper()]
        else:
            raise KeyError('未找到对应的配置信息')
    else:
        raise ValueError('请输入正确的配置名称或配置文件路径')


def save_to_csv(log_info_dic_list, headers, csv_file):
    try:
        with codecs.open(csv_file, "a+", "utf_8_sig") as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=headers)
            csv_writer.writeheader()
            if log_info_dic_list is None:
                logger.info('数据是空的')
            for log_info in log_info_dic_list:
                csv_writer.writerow(log_info)
        logger.info('目标数据存为Excel成功')
    except Exception as exp:
        logger.info(exp.message)


def zip_dir(dir_name, zip_file_name):
    try:
        file_list = []
        if os.path.isfile(dir_name):
            file_list.append((dir_name, os.path.split(dir_name)[1]))
        elif os.path.isdir(dir_name):
            for root, dirs, files in os.walk(dir_name):
                for name in files:
                    full_path = os.path.join(root, name)
                    zip_path = full_path[len(dir_name):]
                    file_list.append((full_path, zip_path))
        with zipfile.ZipFile(zip_file_name, mode='w') as zip_file:
            for f in file_list:
                zip_file.write(f[0], f[1])
        logger.info('目标数据打包为压缩包成功')
    except Exception as exp:
        logger.info(exp.message)

