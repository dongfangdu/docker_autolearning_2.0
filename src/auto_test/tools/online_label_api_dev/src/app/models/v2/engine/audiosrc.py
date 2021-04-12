# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, SmallInteger, Index, DateTime, FetchedValue
from sqlalchemy.dialects.mysql import MEDIUMTEXT

from . import Base


class AudiosrcFileinfo(Base):
    __incomplete_tablename__ = 'audiosrc_fileinfo'

    id = Column(Integer, primary_key=True)
    asrc_uuid = Column(String(64), nullable=False, index=True)
    asrc_url = Column(String(512), nullable=False)
    asrc_md5 = Column(String(64), nullable=False, index=True)
    asrc_size = Column(Integer, nullable=False)
    asrc_mime_type = Column(String(32), nullable=False)
    asrc_rel_path = Column(String(512))
    asrc_upload_time = Column(Integer, index=True)
    upload_uuid = Column(String(64))
    upload_dir = Column(String(512))

    def keys(self):
        return ['id', 'asrc_uuid', 'asrc_url', 'asrc_md5', 'asrc_size', 'asrc_mime_type', 'asrc_rel_path',
                'asrc_upload_time', 'upload_uuid', 'upload_dir', ]

    @staticmethod
    def cvs_keys():
        return ['asrc_uuid', 'asrc_url', 'asrc_md5', 'asrc_size', 'asrc_mime_type', 'asrc_rel_path',
                'asrc_upload_time', 'upload_uuid', 'upload_dir', ]


class AudiosrcFiletrans(Base):
    __incomplete_tablename__ = 'audiosrc_filetrans'

    id = Column(Integer, primary_key=True)
    ng_version = Column(String(64), nullable=False)
    file_uuid = Column(String(64), nullable=False)
    ft_task_id = Column(String(64), index=True)
    ft_status_code = Column(String(64))
    ft_status_text = Column(String(500))
    ft_redis_text = Column(MEDIUMTEXT)
    ft_log_text = Column(MEDIUMTEXT)

    def keys(self):
        return ['id', 'ng_version', 'file_uuid', 'ft_task_id', 'ft_status_code', 'ft_status_text', 'ft_redis_text',
                'ft_log_text', ]
