from sqlalchemy import Column, String, Integer, DateTime, SmallInteger
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from models.base_singleton import DBGlobal

Base = declarative_base(bind=DBGlobal().gen_engine())
_Base = declarative_base(bind=DBGlobal().gen_engine(bind='Test'))

class TrainBase(Base):
    __abstract__ = True

    def __getitem__(self, item):
        return getattr(self, item)

    # def keys(self):
    #     return self.fields

class TestBase(_Base):
    __abstract__ = True

    def __getitem__(self, item):
        return getattr(self, item)


class TrainRequestInfo(TrainBase):
    __tablename__ = 'al_train_request_info'

    insert_time = Column(Integer)
    is_deleted = Column(SmallInteger, default=0)
    id = Column(Integer, primary_key=True)
    train_uuid = Column(String(64), nullable=False)
    train_start_time = Column(Integer)
    train_finish_time = Column(Integer)
    train_status = Column(Integer, nullable=False, default=0)
    train_switch_mode = Column(Integer, nullable=False, default=0)
    train_verbose = Column(MEDIUMTEXT, nullable=False, default=0)

    corpus_uuid = Column(String(64))
    corpus_dir = Column(String(255))

    init_model_uuid = Column(String(64))
    init_model_url = Column(String(255))

    def keys(self):
        return ['id', 'train_uuid', 'train_start_time', 'train_finish_time', 'train_switch_mode', 'train_status',
                'train_verbose', 'corpus_uuid', 'corpus_dir', 'init_model_uuid', 'init_model_url', ]


class TrainModelInfo(TrainBase):
    __tablename__ = 'al_train_model_info'

    insert_time = Column(Integer)
    is_deleted = Column(SmallInteger, default=0)
    id = Column(Integer, primary_key=True)
    model_uuid = Column(String(64), nullable=False)
    model_url = Column(String(255))
    model_create_time = Column(Integer)
    model_status = Column(SmallInteger, nullable=False, default=0)

    train_uuid = Column(String(64), nullable=False)

    def keys(self):
        return ['id', 'model_uuid', 'model_url', 'model_create_time', 'model_status', 'train_uuid', ]

class OverallResultInfo(TestBase):
    __tablename__ = 'al_test_overall_results'

    insert_time = Column(Integer)
    is_deleted = Column(SmallInteger, default=0)
    id = Column(Integer, primary_key=True)
    test_id = Column(String(255))
    model_uuid = Column(String(255))
    model_url = Column(String(255))
    data_uuid = Column(String(255))
    word_err_rate = Column(String(8))

    def keys(self):
        return  ['id', 'word_err_rate', 'test_id', 'model_uuid', 'model_url', 'data_uuid', 'word_err_rate']