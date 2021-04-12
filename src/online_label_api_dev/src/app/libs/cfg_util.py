# -*- coding: utf8 -*-
from ConfigParser import ConfigParser

import os

from app.libs.path_utils import get_project_dir


class ConfigDictParser(ConfigParser):
    def as_dict(self):
        d = dict(self._sections)
        for k, v in d.items():
            d[k] = dict(v)

        return d


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
