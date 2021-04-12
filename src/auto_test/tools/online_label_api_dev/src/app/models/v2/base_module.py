# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declared_attr

from app.models.base import BaseV2, DB_V2_TABLE_PREFIX


class WebBase(BaseV2):
    __bind_key__ = '{}web'.format(DB_V2_TABLE_PREFIX)
    __abstract__ = True
    _the_prefix = '{}'.format(DB_V2_TABLE_PREFIX)

    @declared_attr
    def __tablename__(cls):
        return cls._the_prefix + cls.__incomplete_tablename__


class LabelBase(BaseV2):
    __bind_key__ = '{}label'.format(DB_V2_TABLE_PREFIX)
    __abstract__ = True
    _the_prefix = '{}'.format(DB_V2_TABLE_PREFIX)

    @declared_attr
    def __tablename__(cls):
        return cls._the_prefix + cls.__incomplete_tablename__


class EngineBase(BaseV2):
    __bind_key__ = '{}engine'.format(DB_V2_TABLE_PREFIX)
    __abstract__ = True
    _the_prefix = '{}'.format(DB_V2_TABLE_PREFIX)

    @declared_attr
    def __tablename__(cls):
        return cls._the_prefix + cls.__incomplete_tablename__


class TestBase(BaseV2):
    __bind_key__ = '{}test'.format(DB_V2_TABLE_PREFIX)
    __abstract__ = True
    _the_prefix = '{}'.format(DB_V2_TABLE_PREFIX)

    @declared_attr
    def __tablename__(cls):
        return cls._the_prefix + cls.__incomplete_tablename__


class TrainBase(BaseV2):
    __bind_key__ = '{}train'.format(DB_V2_TABLE_PREFIX)
    __abstract__ = True
    _the_prefix = '{}'.format(DB_V2_TABLE_PREFIX)

    @declared_attr
    def __tablename__(cls):
        return cls._the_prefix + cls.__incomplete_tablename__
