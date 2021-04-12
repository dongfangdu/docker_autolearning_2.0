# -*- coding: utf-8 -*-
import collections
import hashlib
import time
import uuid
from datetime import datetime


def get_uuid():
    guid = uuid.uuid4()
    return str(guid).replace('-', '')


def current_timestamp_sec():
    return int(time.time())


def current_timestamp_ms():
    return int(round(time.time() * 1000))


def namedtuple_with_defaults(typename, field_names, default_values=()):
    """
    可以带初始值的namedtuple

    :param typename:
    :param field_names:
    :param default_values:
    :return:
    """
    T = collections.namedtuple(typename, field_names)
    T.__new__.__defaults__ = (None,) * len(T._fields)
    if isinstance(default_values, collections.Mapping):
        prototype = T(**default_values)
    else:
        prototype = T(*default_values)
    T.__new__.__defaults__ = tuple(prototype)
    return T


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print '%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000)
        return result

    return timed


def datetime2timestamp(datetime_v):
    if not isinstance(datetime_v, datetime):
        return None
    return int(time.mktime(datetime_v.timetuple()))


def mysql_crc64(string):
    """
    用于优化便签的索引，mysql自身已有crc32函数，但如果表较大索引出现碰撞的可能变大，为了有一定的扩展性，
    在mysql数据库扩展了crc64函数，define如下：
    >>>
        DELIMITER $$

        -- DROP FUNCTION IF EXISTS crc64 $$
        CREATE FUNCTION crc64(data LONGTEXT CHARSET utf8) RETURNS BIGINT UNSIGNED
        DETERMINISTIC
        NO SQL
        SQL SECURITY INVOKER
        COMMENT 'Return a 64 bit CRC of given input, as unsigned big integer'

        BEGIN
          RETURN CONV(LEFT(MD5(data), 16), 16, 10);
        END $$

        DELIMITER ;
    >>>
    本函数也跟mysql定义的函数相一致

    :param string:
    :return:
    """
    if isinstance(string, unicode):
        string = string.encode('utf8')

    m2 = hashlib.md5()
    m2.update(string)
    return int('0x%s' % m2.hexdigest()[0:16], 16)
