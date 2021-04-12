# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declared_attr

from app.models.base import BaseVT, DB_V2_TABLE_PREFIX


class WebBase(BaseVT):
    __bind_key__ = '{}web'.format(DB_V2_TABLE_PREFIX)
    __abstract__ = True
    _the_prefix = '{}'.format(DB_V2_TABLE_PREFIX)

    @declared_attr
    def __tablename__(cls):
        return cls._the_prefix + cls.__incomplete_tablename__


class LabelBase(BaseVT):
    __bind_key__ = '{}label'.format(DB_V2_TABLE_PREFIX)
    __abstract__ = True
    _the_prefix = '{}'.format(DB_V2_TABLE_PREFIX)

    @declared_attr
    def __tablename__(cls):
        return cls._the_prefix + cls.__incomplete_tablename__


class EngineBase(BaseVT):
    __bind_key__ = '{}engine'.format(DB_V2_TABLE_PREFIX)
    __abstract__ = True
    _the_prefix = '{}'.format(DB_V2_TABLE_PREFIX)

    @declared_attr
    def __tablename__(cls):
        return cls._the_prefix + cls.__incomplete_tablename__


class TestBase(BaseVT):
    __bind_key__ = '{}test'.format(DB_V2_TABLE_PREFIX)
    __abstract__ = True
    _the_prefix = '{}'.format(DB_V2_TABLE_PREFIX)

    @declared_attr
    def __tablename__(cls):
        return cls._the_prefix + cls.__incomplete_tablename__


class TrainBase(BaseVT):
    __bind_key__ = '{}train'.format(DB_V2_TABLE_PREFIX)
    __abstract__ = True
    _the_prefix = '{}'.format(DB_V2_TABLE_PREFIX)

    @declared_attr
    def __tablename__(cls):
        return cls._the_prefix + cls.__incomplete_tablename__
