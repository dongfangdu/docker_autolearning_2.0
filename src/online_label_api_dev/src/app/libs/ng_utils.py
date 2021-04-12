# -*- coding: utf-8 -*-
import json
import logging

import os
import re
import redis

from app.libs.builtin_extend import magnitude_converter, get_host_ip
from app.libs.cfg_util import get_config_dict

logger = logging.getLogger(__name__)


def get_ng_cfg_value(key):
    ng_cfg_dict = get_config_dict(conf_file='ng_base.ini')
    ng_base_dict = ng_cfg_dict['ASR_NG_BASE']

    return ng_base_dict.get(key)


def get_ng_base_path(is_running=False):
    if is_running:
        command = 'docker inspect nls-cloud-asr -f "{{json .Mounts}}"'

        import subprocess as sp
        child = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        streamdata = child.communicate()
        return_code = child.returncode
        if return_code != 0:
            logger.error(streamdata[1])
            return None

        json_str = streamdata[0]

        mounts_info = json.loads(json_str)
        if isinstance(mounts_info, list):
            for mount in mounts_info:
                if mount.get('Type') == 'bind':
                    return os.path.abspath(mount.get('Source').split('service')[0])
                else:
                    continue
        elif isinstance(mounts_info, dict):
            mount = mounts_info
            if mount.get('Type') == 'bind':
                return os.path.abspath(mount.get('Source').split('service')[0])

        return None
    else:
        return get_ng_cfg_value('ng_base_path')


def get_ng_version():
    ng_version = get_ng_cfg_value('ng_version')
    if ng_version:
        return ng_version

    ng_base_path = get_ng_base_path()

    return get_version_from_base_path(ng_base_path) if ng_base_path else None


def get_ng_host():
    return get_ng_cfg_value('ng_host')


def get_ng_ft_host():
    gateway_port = 8101  # TODO
    return '{}:{}'.format(get_ng_host(), gateway_port)


def get_ng_data_dir(is_running=False):
    return os.path.join(get_ng_base_path(is_running=is_running), 'service/data')


def get_ng_logs_dir(is_running=False):
    return os.path.join(get_ng_base_path(is_running=is_running), 'service/logs')


def get_ng_ft_data_dir(is_running=False):
    return os.path.join(get_ng_data_dir(is_running=is_running), 'servicedata/nls-filetrans')


def get_ng_ft_data_tmp_dir(sys_name, is_running=False):
    tmp_dir = os.path.join(get_ng_ft_data_dir(is_running=is_running), sys_name)
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    return tmp_dir


def get_ng_ft_logs_dir():
    # TODO
    return os.path.join(get_ng_logs_dir(), 'nls-filetrans')


def get_ng_docker_data_dir():
    return '/home/admin/disk'


def get_ng_ft_docker_data_dir():
    return os.path.join(get_ng_docker_data_dir(), 'nls-filetrans')


def get_ng_ft_docker_data_tmp_dir(sys_name):
    tmp_dir = os.path.join(get_ng_ft_docker_data_dir(), sys_name)
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    return tmp_dir


def get_ng_redis_connection():
    host = get_ng_host()
    port = 7011  # TODO
    password = '88630dd3d489a617b635d51ef7eedfe'  # TODO

    return redis.Redis(host=host, port=port, password=password)


def get_version_from_base_path(ng_path):
    sre = re.compile(r'((\d)+(\.(\d)+)+)')
    m = sre.search(ng_path)
    if m:
        return str(m.group(0))
    else:
        return None


def get_ng_sample_rate(is_running=False):
    if is_running:
        sample_rate_cfg = os.path.join(get_ng_base_path(is_running=is_running),
                                       'service/resource/asr/default/models/vad.cfg')
        grep_pattern = 'Waveform2Filterbank::sample-frequency'
        command = 'cat {} | grep {} | cut -d = -f 2'.format(sample_rate_cfg, grep_pattern)

        import subprocess as sp
        child = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        streamdata = child.communicate()
        return_code = child.returncode
        if return_code != 0:
            print streamdata[1]
            return None

        return int(str(streamdata[0]).strip())
    else:
        return magnitude_converter(get_ng_cfg_value('ng_sample_rate') or '16000')


def is_local_ng():
    return get_host_ip() == get_ng_host()



# if __name__ == '__main__':
#     print(get_ng_ft_data_tmp_dir('auto', is_running=True))
#     print(get_ng_ft_data_tmp_dir('auto', is_running=False))
