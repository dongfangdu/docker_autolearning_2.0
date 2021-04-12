# -*- coding: utf-8 -*-
import time
from contextlib import contextmanager
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy
from sqlalchemy import Column, Integer, SmallInteger
from sqlalchemy.ext.declarative import declared_attr


class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


db = SQLAlchemy()


class WebBaseOld(db.Model):
    __bind_key__ = 'al_web'
    __abstract__ = True
    _the_prefix = 'al_'

    insert_time = Column(Integer)
    is_deleted = Column(SmallInteger, default=0)

    @declared_attr
    def __tablename__(cls):
        return cls._the_prefix + cls.__incomplete_tablename__

    def __init__(self):
        self.insert_time = int(time.time())

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def create_datetime(self):
        if self.insert_time:
            return datetime.fromtimestamp(self.insert_time)
        else:
            return None

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

    def delete(self):
        self.is_deleted = 1

    def keys(self):
        return self.fields

    def hide(self, *keys):
        for key in keys:
            self.fields.remove(key)
        return self

    def append(self, *keys):
        for key in keys:
            self.fields.append(key)
        return self


class Base(db.Model):
    __abstract__ = True

    create_time = Column(Integer)
    is_deleted = Column(SmallInteger, default=0)

    def __init__(self):
        self.create_time = int(time.time())

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def create_datetime(self):
        if self.create_time:
            return datetime.fromtimestamp(self.create_time)
        else:
            return None

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

    def delete(self):
        self.is_deleted = 1

    def keys(self):
        return self.fields

    def hide(self, *keys):
        for key in keys:
            self.fields.remove(key)
        return self

    def append(self, *keys):
        for key in keys:
            self.fields.append(key)
        return self


class SimpleBase(db.Model):
    __abstract__ = True

    def __getitem__(self, item):
        return getattr(self, item)

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

    def keys(self):
        return self.fields

    def hide(self, *keys):
        for key in keys:
            self.fields.remove(key)
        return self

    def append(self, *keys):
        for key in keys:
            self.fields.append(key)
        return self


class WebBase(SimpleBase):
    __bind_key__ = 'al_web'
    __abstract__ = True
    _the_prefix = 'al_'

    @declared_attr
    def __tablename__(cls):
        return cls._the_prefix + cls.__incomplete_tablename__


class LabelBase(SimpleBase):
    __bind_key__ = 'al_label'
    __abstract__ = True
    _the_prefix = 'al_'

    @declared_attr
    def __tablename__(cls):
        return cls._the_prefix + cls.__incomplete_tablename__


class EngineBase(SimpleBase):
    __bind_key__ = 'al_engine'
    __abstract__ = True
    _the_prefix = 'al_'

    @declared_attr
    def __tablename__(cls):
        return cls._the_prefix + cls.__incomplete_tablename__


class TestBase(SimpleBase):
    __bind_key__ = 'al_test'
    __abstract__ = True
    _the_prefix = 'al_'

    @declared_attr
    def __tablename__(cls):
        return cls._the_prefix + cls.__incomplete_tablename__


class TrainBase(SimpleBase):
    __bind_key__ = 'al_train'
    __abstract__ = True
    _the_prefix = 'al_'

    @declared_attr
    def __tablename__(cls):
        return cls._the_prefix + cls.__incomplete_tablename__


class LinjrBase(SimpleBase):
    __bind_key__ = 'al_linjr'
    __abstract__ = True
    _the_prefix = 'al_'

    @declared_attr
    def __tablename__(cls):
        return cls._the_prefix + cls.__incomplete_tablename__
