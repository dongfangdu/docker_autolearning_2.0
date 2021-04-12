# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, Time, Index, SmallInteger

from app.models.base import BaseV1


class AudioFile(BaseV1):
    id = Column(Integer, primary_key=True)
    file_uuid = Column(String(32), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_url = Column(String(255), nullable=False)
    file_md5 = Column(String(32))
    rel_path = Column(String(255))
    upload_time = Column(Integer)
    analysis_status = Column(SmallInteger)
    task_id = Column(String(50))
    task_status_code = Column(String(10))
    task_status_text = Column(String(50))

    def keys(self):
        return ['id', 'file_uuid', 'file_name', 'file_url', 'file_md5', 'rel_path', 'upload_time', 'analysis_status',
                'task_id', 'task_status_code', 'task_status_text']


class AudioFileMark(BaseV1):
    id = Column(Integer, primary_key=True)
    file_uuid = Column(String(32), nullable=False)
    mark_key = Column(String(255), nullable=False)
    mark_value = Column(String(255), nullable=False)

    def keys(self):
        return ['id', 'file_uuid', 'mark_key', 'mark_value']


class Utterance(BaseV1):
    id = Column(Integer, primary_key=True)
    request_id = Column(String(50), nullable=False, unique=True)
    path = Column(String(255), nullable=False)
    url = Column(String(255))
    cut_ratio = Column(Numeric(8, 4))
    volume = Column(Numeric(8, 2))
    snr = Column(Numeric(8, 2))
    pre_snr = Column(Numeric(8, 2))
    latter_snr = Column(Numeric(8, 2))
    is_assigned = Column(SmallInteger)

    def keys(self):
        return ['id', 'request_id', 'path', 'url', 'cut_ratio', 'volume', 'snr', 'pre_snr', 'latter_snr', 'create_id',
                'is_assigned']


class UtteranceAlisr(BaseV1):
    id = Column(Integer, primary_key=True)
    time = Column(DateTime, nullable=False)
    request_id = Column(String(50), nullable=False)
    result = Column(String(1024))
    lexical = Column(String(1024))
    lexical_no_symbol = Column(String(1024))

    def keys(self):
        return ['id', 'time', 'request_id', 'result', 'lexical', 'lexical_no_symbol', 'create_id']


class UtteranceTrace(BaseV1):
    id = Column(Integer, primary_key=True)
    request_id = Column(String(64), nullable=False)
    time = Column(DateTime, nullable=False)
    long_type = Column(String(64))
    log_type = Column(String(64))
    app = Column(String(64))
    group = Column(String(64))
    ip = Column(String(16))
    app_key = Column(String(64))
    start_timestamp = Column(String(13))
    end_timestamp = Column(String(13))
    o_date = Column(Date)
    o_time = Column(Time)
    latency = Column(Integer)
    status_code = Column(String(16))
    status_message = Column(String(1024))
    duration = Column(Integer)
    audio_format = Column(String(32))
    audio_url = Column(String(255))
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
    result = Column(String(1024))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    request_time = Column(String(13))
    sample_rate = Column(String(255))
    device_uuid = Column(String(255))

    def keys(self):
        return ['id = ', 'request_id', 'time', 'long_type', 'log_type', 'app', 'group', 'ip', 'app_key',
                'start_timestamp', 'end_timestamp', 'o_date', 'o_time', 'latency', 'status_code', 'status_message',
                'duration', 'audio_format', 'audio_url', 'method', 'packet_count', 'avg_packet_duration', 'total_rtf',
                'raw_rtf', 'real_rtf', 'detect_duration', 'total_cost_time', 'receive_cost_time', 'wait_cost_time',
                'process_time', 'processor_id', 'user_id', 'vocabulary_id', 'keyword_list_id', 'customization_id',
                'class_vocabulary_id', 'result', 'start_time', 'end_time', 'request_time', 'sample_rate',
                'device_uuid', ]


class GatewayAcces(BaseV1):
    __table_args__ = (
        Index('request_id_time', 'time', 'request_id'),
    )

    create_time = Column(Integer)
    is_deleted = Column(SmallInteger)
    id = Column(Integer, primary_key=True)
    time = Column(DateTime, nullable=False)
    logger = Column(String(64))
    app = Column(String(64))
    group = Column(String(64))
    ip = Column(String(16))
    app_key = Column(String(64), nullable=False)
    request_id = Column(String(64), nullable=False)
    session_id = Column(String(64))
    device_uuid = Column(String(64))
    uid = Column(String(64))
    start_timestamp = Column(String(13))
    latency = Column(Integer)
    status_code = Column(String(16))
    status_message = Column(String(1024))
    backend_apps = Column(String(255))
    start_time = Column(DateTime)

    def keys(self):
        return ['create_time', 'is_deleted', 'id', 'time', 'logger', 'app', 'group', 'ip', 'app_key', 'request_id',
                'session_id', 'device_uuid', 'uid', 'start_timestamp', 'latency', 'status_code', 'status_message',
                'backend_apps', 'start_time', ]


class UtteranceAccess(BaseV1):
    __table_args__ = (
        Index('request_id_time', 'request_id', 'time'),
    )

    create_time = Column(Integer)
    is_deleted = Column(SmallInteger)
    id = Column(Integer, primary_key=True)
    request_id = Column(String(64), nullable=False)
    time = Column(DateTime, nullable=False)
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
    result = Column(String(1024))
    group_name = Column(String(64))
    start_time = Column(DateTime)

    def keys(self):
        return ['create_time', 'is_deleted', 'id', 'request_id', 'time', 'app', 'group', 'ip', 'app_key', 'session_id',
                'device_uuid', 'uid', 'start_timestamp', 'latency', 'status_code', 'status_message', 'backend_apps',
                'duration', 'audio_format', 'audio_url', 'sample_rate', 'method', 'packet_count', 'avg_packet_duration',
                'total_rtf', 'raw_rtf', 'real_rtf', 'detect_duration', 'total_cost_time', 'receive_cost_time',
                'wait_cost_time', 'process_time', 'processor_id', 'user_id', 'vocabulary_id', 'keyword_list_id',
                'customization_id', 'class_vocabulary_id', 'result', 'group_name', 'start_time', ]


class UtteranceRestful(BaseV1):
    id = Column(Integer, primary_key=True)
    task_id = Column(String(50), nullable=False, index=True)
    channel_id = Column(Integer)
    begin_time = Column(Integer, index=True)
    end_time = Column(Integer)
    speech_rate = Column(Integer)
    text = Column(String(1024))
    emotion_value = Column(Numeric(8, 3))

    def keys(self):
        return ['create_time', 'is_deleted', 'id', 'task_id', 'channel_id', 'begin_time', 'end_time', 'speech_rate',
                'text', 'emotion_value', ]
