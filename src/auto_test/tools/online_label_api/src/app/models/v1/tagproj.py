# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, SmallInteger, Numeric

from app.models.base import BaseV1


class TagProject(BaseV1):
    id = Column(Integer, primary_key=True)
    proj_code = Column(String(24), unique=True, nullable=False)
    proj_name = Column(String(24), nullable=False)
    create_uid = Column(Integer, nullable=False)
    region_id = Column(Integer, nullable=False)
    proj_desc = Column(String(2000))
    proj_status = Column(SmallInteger, nullable=False, default=0)

    def keys(self):
        return ['id', 'proj_code', 'proj_name', 'create_uid', 'region_id', 'proj_desc', 'proj_status', 'create_time']


class TagTask(BaseV1):
    id = Column(Integer, primary_key=True)
    task_code = Column(String(24), nullable=False, unique=True)
    task_name = Column(String(24), nullable=False)
    proj_id = Column(Integer, nullable=False)
    finish_time = Column(Integer)
    create_uid = Column(Integer)
    tagger_uid = Column(Integer)
    tagging_status = Column(SmallInteger, nullable=False)
    audit_status = Column(SmallInteger, nullable=False)
    task_status = Column(SmallInteger, nullable=False, default=0)

    def keys(self):
        return ['id', 'task_code', 'task_name', 'proj_id', 'finish_time', 'create_uid', 'tagger_uid', 'tagging_status',
                'audit_status', 'task_status', 'create_time']


class TagResult(BaseV1):
    id = Column(Integer, primary_key=True)
    request_id = Column(String(50), nullable=False)
    proj_id = Column(Integer)
    task_id = Column(Integer)
    tag_status = Column(Integer)

    label_text = Column(String(500))
    label_time = Column(Integer)
    insertion_count = Column(Integer)
    sub_count = Column(Integer)
    delete_count = Column(Integer)
    wer = Column(Numeric(8, 4))
    person = Column(String(255))
    accent = Column(String(255))
    gender = Column(String(255))

    def keys(self):
        return ['id', 'request_id', 'proj_id', 'task_id', 'tag_status', 'label_text', 'label_time',
                'insertion_count', 'sub_count', 'delete_count', 'wer', 'person', 'accent', 'gender', 'create_time']
