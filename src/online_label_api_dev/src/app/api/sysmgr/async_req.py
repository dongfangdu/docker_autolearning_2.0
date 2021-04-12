# -*- coding: utf-8 -*-
import json
import logging

from flask import g

from app.libs.builtin_extend import namedtuple_with_defaults, current_timestamp_sec, get_uuid
from app.libs.enums import AsyncReqStatusEnum
from app.models.base import db_v2
from app.models.v2.web.common import AsyncReq

logger = logging.getLogger(__name__)

AsyncReqViewListItemFields = (
    'create_time', 'id', 'task_code', 'task_name', 'proj_id', 'finish_time', 'create_uid', 'tagger_uid', 'task_status')
AsyncReqViewListItem = namedtuple_with_defaults('AsyncReqViewListItem', AsyncReqViewListItemFields,
                                                default_values=(None,) * len(AsyncReqViewListItemFields))


def done_async_req(async_future):
    result = async_future.result()
    if not result:
        logger.error(u'异步回调结果为空，非法')
        return

    req_uuid = result.get('req_uuid')
    async_req = AsyncReq.query.filter_by(req_uuid=req_uuid).first()
    if not async_req:
        logger.error('async request failed, req_uuid: {}'.format(req_uuid))
        return

    with db_v2.auto_commit():
        async_req.req_status = result.get('req_status')
        async_req.req_errno = result.get('req_errno')
        async_req.req_errmsg = result.get('req_errmsg')
        async_req.req_result = result.get('req_result')
        async_req.req_finish_time = current_timestamp_sec()


def create_async_req(req_type):
    async_req = AsyncReq()
    async_req.req_uuid = get_uuid()
    async_req.req_create_time = current_timestamp_sec()
    async_req.req_create_uid = g.user.uid
    async_req.req_type = req_type
    async_req.req_status = AsyncReqStatusEnum.UNSTARTED.value

    with db_v2.auto_commit():
        db_v2.session.add(async_req)

    return async_req.req_uuid


def run_async_req(req_uuid):
    async_req = AsyncReq.query.filter_by(req_uuid=req_uuid).first()
    if not async_req:
        logger.error(u'async_req 不合法的全局ID req_uuid: {}'.format(req_uuid))
        return None
    with db_v2.auto_commit():
        async_req.req_status = AsyncReqStatusEnum.RUNNING.value
    return async_req


def get_async_req_default_future(req_uuid):
    req_status = AsyncReqStatusEnum.RUNNING.value
    req_errno = '1001000'
    req_errmsg = u'正常'
    req_result_dict = {}

    req_result = json.dumps(req_result_dict)
    async_default_future = {
        'req_uuid': req_uuid,
        'req_status': req_status,
        'req_errno': req_errno,
        'req_errmsg': req_errmsg,
        'req_result': req_result,
    }

    return async_default_future
