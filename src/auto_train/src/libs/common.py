# -*- coding:utf-8 -*-
import os
import sys
import uuid
from ConfigParser import ConfigParser

import time


class ConfigDictParser(ConfigParser):
    def as_dict(self):
        d = dict(self._sections)
        for k, v in d.items():
            d[k] = dict(v)

        return d


def get_project_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))


def get_src_dir():
    return os.path.join(get_project_dir(), 'src')


def get_var_dir():
    var_dir = os.path.join(get_project_dir(), 'var')
    if not os.path.exists(var_dir):
        os.makedirs(var_dir, mode=0775)
    return var_dir


def get_tmp_dir():
    tmp_dir = os.path.join(get_project_dir(), 'tmp')
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir, mode=0775)
    return tmp_dir


def get_resource_dir():
    return os.path.join(get_src_dir(), 'resource')


def get_config_dict(conf_file='config.ini', conf_path='./cfg'):
    if conf_path[0] != '/':
        conf_path = os.path.abspath(os.path.join(get_project_dir(), conf_path))
    conf_file = os.path.join(conf_path, conf_file)
    # print conf_file
    if not os.path.exists(conf_file):
        raise RuntimeError(u'配置文件不存在')

    cf = ConfigDictParser()
    cf.read(conf_file)
    # pprint(cf.as_dict())

    return cf.as_dict()


def get_package_path():
    dirname_list = [dirname for dirname in sys.path if 'site-packages' in dirname]
    return os.path.abspath(dirname_list[0]) if len(dirname_list) > 0 else None


def get_db_url():
    cfg = ''


def get_uuid():
    guid = uuid.uuid4()
    return str(guid).replace('-', '')


def current_timestamp_sec():
    return int(time.time())

#
# if __name__ == '__main__':
#     print __file__
