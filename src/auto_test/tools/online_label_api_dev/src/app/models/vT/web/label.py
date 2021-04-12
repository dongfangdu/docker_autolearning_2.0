# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, SmallInteger, Numeric, DateTime, FetchedValue

from . import Base


class LabelProject(Base):
    __incomplete_tablename__ = 'label_project'

    id = Column(Integer, primary_key=True)
    proj_code = Column(String(24), unique=True, nullable=False)
    proj_name = Column(String(24), nullable=False)
    proj_desc = Column(String(2000))
    proj_status = Column(SmallInteger, nullable=False, default=0)
    proj_difficulty = Column(Numeric(8, 3), default=1.0)
    create_uid = Column(Integer, nullable=False)
    create_time = Column(Integer)
    region_id = Column(Integer, nullable=False)
    region_full_ids = Column(String(100), nullable=False)
    region_full_name = Column(String(100), nullable=False)

    def keys(self):
        return ['id', 'proj_code', 'proj_name', 'create_uid', 'create_time', 'proj_desc', 'proj_status',
                'proj_difficulty', 'region_id', 'region_full_ids', 'region_full_name', ]


class LabelTask(Base):
    __incomplete_tablename__ = 'label_task'

    id = Column(Integer, primary_key=True)
    task_code = Column(String(24), nullable=False, unique=True)
    task_name = Column(String(24), nullable=False)
    proj_id = Column(Integer, default=-1)
    create_uid = Column(Integer)
    create_time = Column(Integer)
    task_status = Column(SmallInteger, nullable=False, default=0)
    finish_time = Column(Integer)

    def keys(self):
        return ['id', 'task_code', 'task_name', 'proj_id', 'create_uid', 'create_time', 'task_status', 'finish_time', ]


class LabelUserMap(Base):
    __incomplete_tablename__ = 'label_user_map'

    id = Column(Integer, primary_key=True)
    uid = Column(Integer, nullable=False)
    rel_id = Column(Integer, nullable=False)
    rel_type = Column(SmallInteger, nullable=False, default=0)

    def keys(self):
        return ['id', 'uid', 'rel_id', 'rel_type', ]


class LabelResult(Base):
    __incomplete_tablename__ = 'label_result'

    id = Column(Integer, primary_key=True)
    request_id = Column(String(50), nullable=False)
    uttr_stt_time = Column(Integer)
    uttr_url = Column(String(255))
    uttr_result = Column(String(1024))

    proj_id = Column(Integer)
    proj_code = Column(String(24))
    proj_name = Column(String(24))

    task_id = Column(Integer)
    task_code = Column(String(24))
    task_name = Column(String(24))

    label_status = Column(SmallInteger)
    label_text = Column(String(500))
    label_time = Column(Integer)
    label_uid = Column(Integer)
    label_counter = Column(Integer)

    ins_cnt = Column(Integer)
    sub_cnt = Column(Integer)
    del_cnt = Column(Integer)
    wer = Column(Numeric(8, 4))

    label_tag_person = Column(String(255))
    label_tag_accent = Column(String(255))
    label_tag_gender = Column(String(255))

    def keys(self):
        return ['id', 'request_id', 'uttr_stt_time', 'uttr_url', 'uttr_result', 'proj_id', 'proj_code', 'proj_name',
                'task_id', 'task_code', 'task_name', 'label_status', 'label_text', 'label_time', 'label_uid',
                'label_counter', 'ins_cnt', 'sub_cnt', 'del_cnt', 'wer', 'label_tag_person', 'label_tag_accent',
                'label_tag_gender', ]


class LabelUtteranceInfo(Base):
    __incomplete_tablename__ = 'label_utterance_info'

    ng_version = Column(String(64), nullable=False)
    id = Column(Integer, primary_key=True)
    request_id = Column(String(64), nullable=False, unique=True)
    time = Column(DateTime, nullable=False, index=True)
    app = Column(String(64))
    group = Column(String(64))
    ip = Column(String(16))
    app_key = Column(String(64))
    session_id = Column(String(64))
    device_uuid = Column(String(64))
    uid = Column(String(64))
    start_timestamp = Column(String(13))
    latency = Column(Integer)
    status_code = Column(String(16))
    status_message = Column(String(1024))
    backend_apps = Column(String(255))
    duration = Column(Integer)
    audio_format = Column(String(32))
    audio_url = Column(String(255))
    sample_rate = Column(Integer)
    method = Column(String(64))
    packet_count = Column(Integer)
    avg_packet_duration = Column(Integer)
    total_rtf = Column(Numeric(8, 3))
    raw_rtf = Column(Numeric(8, 3))
    real_rtf = Column(Numeric(8, 3))
    detect_duration = Column(Integer)
    total_cost_time = Column(Integer)
    receive_cost_time = Column(Integer)
    wait_cost_time = Column(Integer)
    process_time = Column(Integer)
    processor_id = Column(Integer)
    user_id = Column(String(64))
    vocabulary_id = Column(String(64))
    keyword_list_id = Column(String(64))
    customization_id = Column(String(64))
    class_vocabulary_id = Column(String(64))
    result = Column(String(1024), nullable=False)
    group_name = Column(String(64))
    path = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)
    truncation_ratio = Column(Numeric(8, 4))
    volume = Column(Numeric(8, 2))
    snr = Column(Numeric(8, 2))
    pre_snr = Column(Numeric(8, 2))
    post_snr = Column(Numeric(8, 2))
    is_assigned = Column(SmallInteger)
    uttr_status = Column(SmallInteger)
    prepare_uuid = Column(String(64))

    def keys(self):
        return ['ng_version', 'id', 'request_id', 'time', 'app', 'group', 'ip', 'app_key', 'session_id', 'device_uuid',
                'uid', 'start_timestamp', 'latency', 'status_code', 'status_message', 'backend_apps', 'duration',
                'audio_format', 'audio_url', 'sample_rate', 'method', 'packet_count', 'avg_packet_duration',
                'total_rtf', 'raw_rtf', 'real_rtf', 'detect_duration', 'total_cost_time', 'receive_cost_time',
                'wait_cost_time', 'process_time', 'processor_id', 'user_id', 'vocabulary_id', 'keyword_list_id',
                'customization_id', 'class_vocabulary_id', 'result', 'group_name', 'path', 'url', 'truncation_ratio',
                'volume', 'snr', 'pre_snr', 'post_snr', 'is_assigned', 'uttr_status', 'prepare_uuid']


class LabelDitingInfo(Base):
    __incomplete_tablename__ = 'label_diting_info'

    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime)
    uuid = Column(String(64), nullable=False)
    request_id = Column(String(64), nullable=False, unique=True)
    end_time = Column(DateTime)
    http_cost_time = Column(Integer)
    trans_delay = Column(Integer)
    related_status = Column(SmallInteger, server_default=FetchedValue())
    time = Column(DateTime)
    line_id = Column(String(128))
    case_id = Column(String(64))
    court_id = Column(String(64))
    role_id = Column(String(64))

    def keys(self):
        return ['id', 'start_time', 'uuid', 'request_id', 'end_time', 'http_cost_time', 'trans_delay', 'related_status',
                'time', 'line_id', 'case_id', 'court_id', 'role_id', ]
