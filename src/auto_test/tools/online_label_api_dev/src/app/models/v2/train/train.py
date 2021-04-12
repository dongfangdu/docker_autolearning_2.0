# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Numeric, DateTime, FetchedValue, SmallInteger

from . import Base


class TrainModelInfo(Base):
    __incomplete_tablename__ = 'train_model_info'

    id = Column(Integer, primary_key=True)
    model_uuid = Column(String(64), nullable=False, index=True)
    model_url = Column(String(255), nullable=False)
    model_create_time = Column(Integer)
    model_status = Column(SmallInteger, nullable=False, server_default=FetchedValue())
    train_uuid = Column(String(64), nullable=False, index=True)


class TrainRequestInfo(Base):
    __incomplete_tablename__ = 'train_request_info'

    id = Column(Integer, primary_key=True)
    train_uuid = Column(String(64), nullable=False, index=True)
    train_start_time = Column(Integer)
    train_finish_time = Column(Integer)
    train_status = Column(SmallInteger, nullable=False, server_default=FetchedValue())
    corpus_uuid = Column(String(64), index=True)
    corpus_dir = Column(String(255))
    init_model_uuid = Column(String(64))
    init_model_url = Column(String(255))
