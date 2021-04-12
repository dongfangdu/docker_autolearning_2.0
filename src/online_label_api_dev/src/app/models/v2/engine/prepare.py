# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, SmallInteger, Numeric

from . import Base


# from app.models.base import EngineBase as Base


class PrepareDataInfo(Base):
    __incomplete_tablename__ = 'prepare_data_info'

    id = Column(Integer, primary_key=True)
    prepare_uuid = Column(String(64), nullable=False)
    pdata_uuid = Column(String(64), nullable=False)
    pdata_src_type = Column(SmallInteger, nullable=False)
    pdata_url = Column(String(255), nullable=False)
    pdata_text = Column(String(1024), nullable=False)

    # 下面的字段，用于追溯和统计
    request_id = Column(String(64))
    uttr_url = Column(String(255))
    uttr_result = Column(String(1024))
    uttr_duration = Column(Integer)
    label_uuid = Column(String(64))
    label_text = Column(String(500))


class PrepareRequestInfo(Base):
    __incomplete_tablename__ = 'prepare_request_info'

    id = Column(Integer, primary_key=True)
    is_deleted = Column(SmallInteger)
    prepare_uuid = Column(String(64))
    prepare_start_time = Column(Integer)
    prepare_finish_time = Column(Integer)
    prepare_status = Column(SmallInteger, nullable=False, default=0)
    prepare_type = Column(SmallInteger)
    prepare_data_path = Column(String(1024))


class PrepareChoiceParam(Base):
    __incomplete_tablename__ = 'prepare_choice_param'

    id = Column(Integer, primary_key=True)
    request_id = Column(String(64), nullable=False)
    choice_type = Column(SmallInteger, nullable=False)
    choice_value = Column(Numeric(8, 3))


class PrepareChoiceRule(Base):
    __incomplete_tablename__ = 'prepare_choice_rule'

    id = Column(Integer, primary_key=True)
    choice_type = Column(SmallInteger, nullable=False)
    rule_logic = Column(String(10))
    rule_op_type = Column(String(10))
    rule_op_threshold = Column(Numeric(8, 3))
    rule_order = Column(Integer)
