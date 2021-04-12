# -*- coding: utf-8 -*-
import os


def get_project_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))


def get_src_dir():
    return os.path.join(get_project_dir(), 'src')


def get_cfg_dir():
    return os.path.join(get_project_dir(), 'cfg')


def get_resource_dir():
    return os.path.join(get_src_dir(), 'resource')


def get_bin_dir():
    return os.path.join(get_project_dir(), 'bin')


def get_var_dir():
    var_dir = os.path.join(get_project_dir(), 'var')
    if not os.path.exists(var_dir):
        os.makedirs(var_dir, mode=0775)
    return var_dir


def get_tmp_dir():
    var_dir = os.path.join(get_project_dir(), 'tmp')
    if not os.path.exists(var_dir):
        os.makedirs(var_dir, mode=0775)
    return var_dir

