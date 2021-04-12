# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, SmallInteger, Index, DateTime, FetchedValue

from src.app.models.base import EngineBase as Base


class NgBakFile(Base):
    __incomplete_tablename__ = 'ng_bak_files'
    __table_args__ = (
        Index('uni_name_time', 'file_name', 'origin_st_mtime'),
    )

    id = Column(Integer, primary_key=True)
    file_name = Column(String(128), nullable=False)
    path = Column(String(1024), nullable=False)
    origin_st_mtime = Column(Integer, nullable=False)
    st_size = Column(Integer, nullable=False)
    type = Column(String(16), nullable=False)
    ng_version = Column(String(64))

    def keys(self):
        return ['id', 'file_name', 'path', 'origin_st_mtime', 'st_size', 'type', 'ng_version', ]


class NgDiting(Base):
    __incomplete_tablename__ = 'ng_diting'

    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime)
    uuid = Column(String(64), nullable=False)
    request_id = Column(String(64), nullable=False, unique=True)
    end_time = Column(DateTime)
    http_cost_time = Column(Integer)
    trans_delay = Column(Integer)
    related_status = Column(SmallInteger, server_default=FetchedValue())

    def keys(self):
        return ['id', 'start_time', 'uuid', 'request_id', 'end_time', 'http_cost_time', 'trans_delay',
                'related_status', ]


class NgDitingRelation(Base):
    __incomplete_tablename__ = 'ng_diting_relation'

    id = Column(Integer, primary_key=True)
    time = Column(DateTime)
    uuid = Column(String(64), nullable=False, unique=True)
    line_id = Column(String(128))
    case_id = Column(String(64))
    court_id = Column(String(64))
    role_id = Column(String(64))

    def keys(self):
        return ['id', 'time', 'uuid', 'line_id', 'case_id', 'court_id', 'role_id', ]


class NgTransDelayInfo(Base):
    __incomplete_tablename__ = 'ng_trans_delay_info'
    __table_args__ = (
        Index('idx_line_id_time', 'line_id', 'send_time'),
    )

    id = Column(Integer, primary_key=True)
    line_id = Column(String(128), nullable=False)
    case_id = Column(String(64))
    role_id = Column(String(64))
    court_id = Column(String(64))
    pkg_cnt = Column(Integer, nullable=False)
    send_time = Column(DateTime, nullable=False)
    receive_time = Column(DateTime, nullable=False)
    delay = Column(Integer, nullable=False)
    related_status = Column(SmallInteger, server_default=FetchedValue())

    def keys(self):
        return ['id', 'line_id', 'case_id', 'role_id', 'court_id', 'pkg_cnt', 'send_time', 'receive_time', 'delay',
                'related_status', ]
