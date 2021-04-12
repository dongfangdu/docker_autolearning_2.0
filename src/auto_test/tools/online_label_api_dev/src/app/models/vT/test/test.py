# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Numeric, DateTime, FetchedValue

from . import Base


class TestAsrAudioInfo(Base):
    __incomplete_tablename__ = 'test_asr_audio_info'

    id = Column(Integer, primary_key=True)
    data_uuid = Column(String(255))
    request_id = Column(String(50), nullable=False, unique=True)
    path = Column(String(255), nullable=False)
    url = Column(String(255))
    cut_ratio = Column(Numeric(8, 4))
    volume = Column(Numeric(8, 2))
    snr = Column(Numeric(8, 2))
    pre_snr = Column(Numeric(8, 2))
    latter_snr = Column(Numeric(8, 2))
    label_text = Column(String(1024))
    person = Column(String(255))
    accent = Column(String(255))
    gender = Column(Integer)
    task_id = Column(String(255))
    res_text = Column(String(255))
    par_log_text = Column(String(255))
    tot_words = Column(Integer)
    cor_words = Column(Integer)
    word_cor_rate = Column(Numeric(8, 2))
    word_err_rate = Column(Numeric(8, 2))
    ins_cnt = Column(Integer)
    del_cnt = Column(Integer)
    sub_cnt = Column(Integer)
    total_rtf = Column(Numeric(8, 3))
    raw_rtf = Column(Numeric(8, 3))
    real_rtf = Column(Numeric(8, 3))
    duration = Column(Integer)

    def keys(self):
        return ['id', 'data_uuid', 'request_id', 'path', 'url', 'cut_ratio', 'volume', 'snr', 'pre_snr', 'latter_snr',
                'label_text', 'person', 'accent', 'gender', 'task_id', 'res_text', 'par_log_text', 'tot_words',
                'cor_words', 'word_cor_rate', 'word_err_rate', 'ins_cnt', 'del_cnt', 'sub_cnt', 'total_rtf', 'raw_rtf',
                'real_rtf', 'duration', ]


class TestOverallResult(Base):
    __incomplete_tablename__ = 'test_overall_results'

    id = Column(Integer, primary_key=True)
    test_id = Column(String(255))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    model_uuid = Column(String(255))
    model_url = Column(String(255))
    data_uuid = Column(String(255))
    word_err_rate = Column(Numeric(8, 2))
    tot_word_err_cnt = Column(Integer)
    tot_word_cnt = Column(Integer)
    ins_cnt = Column(Integer)
    del_cnt = Column(Integer)
    sub_cnt = Column(Integer)
    sent_err_rate = Column(Numeric(8, 2))
    err_sent_cnt = Column(Integer)
    tot_sent_cnt = Column(Integer)

    def keys(self):
        return ['id', 'test_id', 'start_time', 'end_time', 'model_uuid', 'model_url', 'data_uuid', 'word_err_rate',
                'tot_word_err_cnt', 'tot_word_cnt', 'ins_cnt', 'del_cnt', 'sub_cnt', 'sent_err_rate', 'err_sent_cnt',
                'tot_sent_cnt', ]


class TestResultBySentence(Base):
    __incomplete_tablename__ = 'test_result_by_sentence'

    id = Column(Integer, primary_key=True)
    test_id = Column(String(255))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    model_uuid = Column(String(255))
    data_uuid = Column(String(255))
    task_id = Column(String(255))
    request_id = Column(String(255))
    path = Column(String(255))
    url = Column(String(255))
    tot_words = Column(Integer)
    cor_words = Column(Integer)
    word_cor_rate = Column(Numeric(8, 2))
    word_err_rate = Column(Numeric(8, 2))
    ins_cnt = Column(Integer)
    del_cnt = Column(Integer)
    sub_cnt = Column(Integer)
    label_text = Column(String(1024))
    recog_text = Column(String(1024), server_default=FetchedValue())
    par_log_text = Column(String(1024))
    total_rtf = Column(Numeric(8, 2))
    raw_rtf = Column(Numeric(8, 2))
    real_rtf = Column(Numeric(8, 2))
    duration = Column(Numeric(8, 2))

    def keys(self):
        return ['id', 'test_id', 'start_time', 'end_time', 'model_uuid', 'data_uuid', 'task_id', 'request_id', 'path',
                'url', 'tot_words', 'cor_words', 'word_cor_rate', 'word_err_rate', 'ins_cnt', 'del_cnt', 'sub_cnt',
                'label_text', 'recog_text', 'par_log_text', 'total_rtf', 'raw_rtf', 'real_rtf', 'duration', ]
