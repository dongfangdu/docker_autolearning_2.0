# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, SmallInteger, FetchedValue

from . import Base


class Region(Base):
    __incomplete_tablename__ = 'common_region'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    parent_id = Column(Integer, nullable=False)
    level = Column(SmallInteger, default=-1)

    def keys(self):
        return ['id', 'name', 'parent_id', 'level']


class Tag(Base):
    __incomplete_tablename__ = 'common_tag'

    id = Column(Integer, primary_key=True)
    tag_uuid = Column(String(64), nullable=False)
    tag_name = Column(String(50), nullable=False)
    tag_ikey = Column(Integer, nullable=False)

    def keys(self):
        return ['id', 'tag_uuid', 'tag_name']


class AsyncReq(Base):
    __incomplete_tablename__ = 'common_async_req'

    id = Column(Integer, primary_key=True)
    req_uuid = Column(String(64), nullable=False)
    req_type = Column(SmallInteger, nullable=False, server_default=FetchedValue())
    req_create_uid = Column(Integer)
    req_create_time = Column(Integer)
    req_finish_time = Column(Integer)
    req_status = Column(SmallInteger)
    req_errno = Column(String(15))
    req_errmsg = Column(String(1024))
    req_result = Column(String(5000))

    def keys(self):
        return ['id', 'req_uuid', 'req_type', 'req_create_uid', 'req_create_time', 'req_finish_time', 'req_status',
                'req_errno', 'req_errmsg', 'req_result', ]
