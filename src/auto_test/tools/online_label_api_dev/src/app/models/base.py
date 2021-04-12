# -*- coding: utf-8 -*-
import traceback
from contextlib import contextmanager

import time
from datetime import datetime
from flask_executor import Executor
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, BaseQuery
from sqlalchemy import inspect, Column, Integer, SmallInteger, orm
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.libs.builtin_extend import current_timestamp_sec
from app.libs.error_code import NotFound, AuthFailed
from app.models.db_utils import get_db_system_prefix, get_db_cfg_dict, get_db_system_short_prefix


class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_bind_names(self, app=None):
        app = self.get_app(app)
        binds = [None] + list(app.config.get('SQLALCHEMY_BINDS') or ())
        return binds

    def check_db_connections(self, app=None):
        bind_names = self.get_bind_names(app=app)
        current_bind = None
        try:
            for check_bind in bind_names:
                current_bind = check_bind
                sessionmaker(db_v2.get_engine(app=app, bind=check_bind))().execute('Select 1').fetchall()
        except SQLAlchemyError as e:
            app.logger.error(traceback.format_exc())
            app.logger.error(e.message)
            raise RuntimeError(u'数据库配置不正确：{}'.format(current_bind))


class Query(BaseQuery):
    def filter_by(self, with_deleted=False, **kwargs):
        if not with_deleted:
            if 'is_deleted' not in kwargs.keys():
                kwargs['is_deleted'] = 0
        return super(Query, self).filter_by(**kwargs)

    def get_or_404(self, ident):
        rv = self.get(ident)
        if not rv:
            raise NotFound()
        return rv

    def first_or_404(self):
        rv = self.first()
        if not rv:
            raise NotFound()
        return rv

    def first_or_4010(self, msg='权限认证失败', error_code=4010):
        rv = self.first()
        if not rv:
            raise AuthFailed(msg=msg, error_code=error_code)
        return rv


db_v1 = SQLAlchemy(query_class=Query)
db_v2 = SQLAlchemy(query_class=Query)
db_vT = SQLAlchemy(query_class=Query)   # 用于迁移数据
# DB_V2_SYSTEM_PREFIX = 'onlinemaintain_'
# DB_V2_TABLE_PREFIX = 'om_'
# DB_V2_SYSTEM_PREFIX = 'onlinelable_'
# DB_V2_TABLE_PREFIX = 'oll_'
DB_V2_SYSTEM_PREFIX = get_db_system_prefix(get_db_cfg_dict())
DB_V2_TABLE_PREFIX = get_db_system_short_prefix(get_db_cfg_dict())
DB_VT_SYSTEM_PREFIX = get_db_system_prefix(get_db_cfg_dict('TRANSFER_SRC'))
DB_VT_TABLE_PREFIX = get_db_system_short_prefix(get_db_cfg_dict('TRANSFER_SRC'))


class BaseV1(db_v1.Model):
    __abstract__ = True

    is_deleted = Column(SmallInteger, default=0)
    create_time = Column(Integer)

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


class BaseV2(db_v2.Model):
    __abstract__ = True
    # is_deleted 必须排在 insert_time前面，因为is_deleted非空，在分页模块的计算count中，第一列必须非空
    is_deleted = Column(SmallInteger, nullable=False, default=0)
    insert_time = Column(Integer)

    def __init__(self):
        self.insert_time = current_timestamp_sec()

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


class BaseVT(db_vT.Model):
    __abstract__ = True
    # is_deleted 必须排在 insert_time前面，因为is_deleted非空，在分页模块的计算count中，第一列必须非空
    is_deleted = Column(SmallInteger, nullable=False, default=0)
    insert_time = Column(Integer)

    def __init__(self):
        self.insert_time = current_timestamp_sec()

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


class MixinJSONSerializer:
    @orm.reconstructor
    def init_on_load(self):
        self._fields = []
        # self._include = []
        self._exclude = []

        self._set_fields()
        self.__prune_fields()

    def _set_fields(self):
        pass

    def __prune_fields(self):
        columns = inspect(self.__class__).columns
        if not self._fields:
            all_columns = set(columns.keys())
            self._fields = list(all_columns - set(self._exclude))

    def hide(self, *args):
        for key in args:
            self._fields.remove(key)
        return self

    def keys(self):
        return self._fields

    def __getitem__(self, key):
        return getattr(self, key)


# 异步处理
asynchronous_executor = Executor(name='asynchronous')
# 多线程处理
transfer_executor = Executor(name='transfer')
