from sqlalchemy import Column, Integer, String, SmallInteger, DateTime, Numeric, FetchedValue

from src.app.models.base import LinjrBase as Base


class PrepareTestData(Base):
    __incomplete_tablename__ = 'test_asr_audio_info'

    id = Column(Integer, primary_key=True)
    prepare_uuid = Column('data_uuid', String(64), nullable=False)
    request_id = Column(String(50), nullable=False)
    path = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)
    label_text = Column(String(1024), nullable=False)

    def keys(self):
        return ['id', 'prepare_uuid', 'request_id', 'path', 'url', 'label_text', ]
