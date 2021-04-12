# -*- coding:utf-8 -*-
import traceback

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from libs.common import get_config_dict
from libs.global_logger import get_logger

logger = get_logger(__name__)


class DBGlobal(object):
    __instance = None
    __engines = {}

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def gen_engine(self, bind=None):
        bind = bind or 'default'
        if not DBGlobal.__engines.get(bind, None):
            db_info_dict = get_config_dict().get('DataBase_{}'.format(bind), None)
            if not db_info_dict:
                logger.error(u'数据库配置缺失，bind: {}'.format(bind))
            try:
                engine = create_engine(
                    'mysql+{driver}://{username}:{password}@{host}:{port}/{database}?charset={charset}'.format(
                        **db_info_dict),
                    pool_size=100,
                    max_overflow=100,
                    pool_recycle=2,
                    echo=False
                )
                # if db_info_dict.get('charset'):
                #     engine.execute("SET NAMES {charset};".format(charset=db_info_dict['charset']))
                DBGlobal.__engines[bind] = engine
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error(u'数据库配置不正确: {}'.format(e.message))
        return DBGlobal.__engines[bind]

    def db_session(self, bind=None):
        engine = DBGlobal().gen_engine(bind=bind)
        SessionFactory = scoped_session(sessionmaker(bind=engine))
        return SessionFactory()

    # @contextmanager
    # def auto_commit(self):
    #     try:
    #         yield
    #         self.db_session().commit()
    #     except Exception as e:
    #         self.db_session().rollback()
    #         raise e


db = DBGlobal()
