# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, DateTime

from app.models.base import BaseV1


class AlNgDitingRelation(BaseV1):
    id = Column(Integer, primary_key=True)
    time = Column(DateTime)
    uuid = Column(String(255), nullable=False)
    line_id = Column(String(255))
    case_id = Column(String(255))
    court_id = Column(String(255))
    role_id = Column(String(255))

    def keys(self):
        return ['id', 'time', 'uuid', 'line_id', 'case_id', 'court_id', 'role_id']


class AlNgDiting(BaseV1):
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime)
    uuid = Column(String(255), nullable=False)
    request_id = Column(String(255), nullable=False)
    end_time = Column(DateTime)
    http_cost_time = Column(Integer)
    trans_delay = Column(Integer)
    related_status = Column(Integer)

    def keys(self):
        return ['id', 'start_time', 'uuid', 'request_id', 'end_time', 'http_cost_time',
                'trans_delay', 'related_status']


class OmAsyncParserTask(BaseV1):
    id = Column(Integer, primary_key=True)
    start_time = Column(Integer)
    finish_time = Column(Integer)
    create_uid = Column(Integer)
    parser_status = Column(Integer)
    result_msg = Column(String(1024))

    def keys(self):
        return ['id', 'start_time', 'finish_time', 'create_uid', 'parser_status', 'result_msg']


class OmAsyncDownloadTask(BaseV1):
    id = Column(Integer, primary_key=True)
    start_time = Column(Integer)
    finish_time = Column(Integer)
    create_uid = Column(Integer)
    download_status = Column(Integer)
    result_msg = Column(String(1024))
    download_path = Column(String(1024))

    def keys(self):
        return ['id', 'start_time', 'finish_time', 'create_uid', 'download_status', 'result_msg', 'download_path']
