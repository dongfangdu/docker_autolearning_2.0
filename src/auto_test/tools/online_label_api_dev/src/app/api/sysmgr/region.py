# -*- coding: utf-8 -*-
import logging

from sqlalchemy.orm import aliased

from app.libs.error_code import ResultSuccess
from app.libs.redprint import Redprint
from app.models.base import db_v2
from app.models.v2.web.common import Region

api = Redprint('region')
logger = logging.getLogger(__name__)


@api.route('/choices-province', methods=['GET'])
def region_choices_province():
    region_objs = Region.query.filter_by(parent_id=0).all()
    vms = []
    for region in region_objs:
        vm = {'k': region.id, 'v': region.name}
        vms.append(vm)
    return ResultSuccess(msg=u'国内省份字典', data=vms)


@api.route('/choices-city', methods=['GET'])
def region_choices_city():
    province = aliased(Region)
    city = aliased(Region)
    rvs = db_v2.session.query(city.id, city.name).filter(city.parent_id == province.id).filter(
        province.parent_id == 0).filter_by().all()
    vms = []
    for k, v in rvs:
        vm = {'k': k, 'v': v}
        vms.append(vm)
    return ResultSuccess(msg=u'国内城市字典', data=vms)


@api.route('/choices-city/<int:province_id>', methods=['GET'])
def region_choices_city_by_province(province_id):
    province = aliased(Region)
    city = aliased(Region)
    rvs = db_v2.session.query(city.id, city.name).filter(city.parent_id == province.id).filter(
        province.id == province_id).filter_by().all()
    vms = []
    for k, v in rvs:
        vm = {'k': k, 'v': v}
        vms.append(vm)
    return ResultSuccess(msg=u'省内城市字典', data=vms)


@api.route('/choices-county/<int:city_id>', methods=['GET'])
def region_choices_county(city_id):
    province = aliased(Region)
    city = aliased(Region)
    county = aliased(Region)
    rvs = db_v2.session.query(county.id, county.name).filter(county.parent_id == city.id).filter(
        city.id == city_id).filter_by().all()
    vms = []
    for k, v in rvs:
        vm = {'k': k, 'v': v}
        vms.append(vm)
    return ResultSuccess(msg=u'市内县城字典', data=vms)


@api.route('/cascade', methods=['GET'])
def region_cascade():
    rvs = Region.query.filter_by().all()

    p_cascade_map = {}
    for rv in rvs:
        parent_id = rv['parent_id']
        p_cascade_item = p_cascade_map.get(parent_id, [])
        child = dict(
            id=rv['id'],
            name=rv['name'],
            level=rv['level']
        )
        p_cascade_item.append(child)
        p_cascade_map[parent_id] = p_cascade_item

    res = _region_iter(p_cascade_map, 0)

    return ResultSuccess(msg=u'区域层级字典', data=res)


def _region_iter(p_cascade_map, p_key):
    region_list = p_cascade_map.pop(p_key, [])
    for region in region_list:
        id = region['id']
        child_list = _region_iter(p_cascade_map, id)
        if len(child_list) > 0:
            region['childs'] = child_list
    return region_list


@api.route('/fullname/<int:region_id>', methods=['GET'])
def region_full(region_id):
    full_name = _region_fullname(region_id)
    return ResultSuccess(msg='test', data=full_name)


def _region_fullname(region_id):
    names = []
    _region_names_iter(region_id, names)
    return ''.join(names)


def _region_names_iter(region_id, names):
    region = Region.query.filter_by(id=region_id).first()
    if region:
        _region_names_iter(region.parent_id, names)
        names.append(region.name)
    return names
