# -*- coding: utf-8 -*-
import os


def get_project_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))


def get_enh_dir():
    return os.path.abspath(os.path.join(get_project_dir(), 'enhance'))


def get_cfg_dir():
    return os.path.join(get_project_dir(), 'cfg')


def get_enhance_tools_dir():
    return get_enh_dir()
