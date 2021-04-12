# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, SmallInteger, Numeric, DateTime

from .import Base


class LabelrawResult(Base):
    __incomplete_tablename__ = 'labelraw_result'

    id = Column(Integer, primary_key=True)
    label_uuid = Column(String(64), nullable=False)

    label_text = Column(String(500))
    label_time = Column(Integer)

    request_id = Column(String(50), nullable=False)
    uttr_url = Column(String(255))

    def keys(self):
        return ['id', 'label_uuid', 'label_text', 'label_time', 'request_id', 'uttr_url', ]


class LabelrawUtteranceInfo(Base):
    __incomplete_tablename__ = 'labelraw_utterance_info'

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
    uttr_status = Column(SmallInteger)

    def keys(self):
        return ['ng_version', 'id', 'request_id', 'time', 'app', 'group', 'ip', 'app_key', 'session_id', 'device_uuid',
                'uid', 'start_timestamp', 'latency', 'status_code', 'status_message', 'backend_apps', 'duration',
                'audio_format', 'audio_url', 'sample_rate', 'method', 'packet_count', 'avg_packet_duration',
                'total_rtf', 'raw_rtf', 'real_rtf', 'detect_duration', 'total_cost_time', 'receive_cost_time',
                'wait_cost_time', 'process_time', 'processor_id', 'user_id', 'vocabulary_id', 'keyword_list_id',
                'customization_id', 'class_vocabulary_id', 'result', 'group_name', 'path', 'url', 'truncation_ratio',
                'volume', 'snr', 'pre_snr', 'post_snr', 'uttr_status', ]
