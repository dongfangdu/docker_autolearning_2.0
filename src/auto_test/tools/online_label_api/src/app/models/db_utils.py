# -*- coding: utf-8 -*-
from collections import defaultdict
from pprint import pprint

from app.libs.builtin_extend import merge_dicts
from app.libs.cfg_util import get_config_dict


def get_db_cfg_dict(keys_type='COMMON'):
    db_cfg_dict = get_config_dict(conf_file='db_base.ini')
    return db_cfg_dict['DATABASE_{}'.format(keys_type)]


def get_db_connect_url(db_cfg):
    connect_url_temp = '{protocol}://{username}:{password}@{host}:{port}'
    connect_url = connect_url_temp.format(**db_cfg)
    return connect_url


def get_db_params(db_cfg):
    param_list = []
    for k, v in db_cfg.items():
        if str(k).startswith('param_') and v and (not not v.strip()):
            param_list.append('{}={}'.format(str(k).replace('param_', ''), v))
    return '&'.join(param_list)


def get_db_company_prefix(db_cfg):
    company_prefix = ''
    company_name_short = db_cfg.get('company_name_short')
    if company_name_short and not not company_name_short.strip():
        company_prefix = '{}_'.format(company_name_short)
    return company_prefix


def get_db_system_prefix(db_cfg):
    system_prefix = ''
    system_name = db_cfg.get('system_name')
    if system_name and not not system_name.strip():
        system_prefix = '{}_'.format(system_name)
    return system_prefix


def get_db_system_short_prefix(db_cfg):
    system_short_prefix = ''
    system_name_short = db_cfg.get('system_name_short')
    if system_name_short and not not system_name_short.strip():
        system_short_prefix = '{}_'.format(system_name_short)
    return system_short_prefix


def get_db_subsystem_list(db_cfg):
    subsystem_list = []
    subsystem_name_list = db_cfg.get('subsystem_name_list')
    if not subsystem_name_list or not subsystem_name_list.strip():
        return subsystem_list
    subsystem_list = str(subsystem_name_list).split(',')
    return subsystem_list


def get_db_list(keys_type='COMMON'):
    db_name_list = []
    db_cfg_common = get_db_cfg_dict(keys_type)

    subsystem_list = get_db_subsystem_list(db_cfg_common)
    if len(subsystem_list) < 1:
        return db_name_list

    company_prefix = get_db_company_prefix(db_cfg_common)
    system_prefix = get_db_system_prefix(db_cfg_common)

    for subsystem_name in subsystem_list:
        db_name_list.append('{company_prefix}{system_prefix}{subsystem_name}'.format(
            company_prefix=company_prefix,
            system_prefix=system_prefix,
            subsystem_name=subsystem_name,
        ))

    return db_name_list


def get_db_binds_dict(keys_type='COMMON'):
    binds_dict = defaultdict(str)
    db_cfg_common = get_db_cfg_dict(keys_type)

    subsystem_list = get_db_subsystem_list(db_cfg_common)
    if len(subsystem_list) < 1:
        return binds_dict

    system_short_prefix = get_db_system_short_prefix(db_cfg_common)

    connect_url = get_db_connect_url(db_cfg_common)
    params_url = get_db_params(db_cfg_common)
    company_prefix = get_db_company_prefix(db_cfg_common)
    system_prefix = get_db_system_prefix(db_cfg_common)
    db_name_temp = '{connect_url}/{company_prefix}{system_prefix}{{subsystem_name}}?{params_url}'.format(
        connect_url=connect_url,
        company_prefix=company_prefix,
        system_prefix=system_prefix,
        params_url=params_url,

    )
    for subsystem_name in subsystem_list:
        k = '{system_short_prefix}{subsystem_name}'.format(
            system_short_prefix=system_short_prefix,
            subsystem_name=subsystem_name,
        )
        v = db_name_temp.format(subsystem_name=subsystem_name)
        binds_dict[k]=v

    return dict(binds_dict)


# if __name__ == '__main__':
#     # print get_db_cfg_dict()
#     # print get_db_connect_url('TRANSFER_SRC')
#     # print get_db_list()
#     # print len(get_db_binds_dict())
#     a = merge_dicts(get_db_binds_dict(), get_db_binds_dict('TRANSFER_SRC'))
#     pprint(a)
#     get_db_params(get_db_cfg_dict())
#
#     print get_db_system_prefix(get_db_cfg_dict())
#     print get_db_system_short_prefix(get_db_cfg_dict())
