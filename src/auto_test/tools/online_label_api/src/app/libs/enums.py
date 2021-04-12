# -*- coding: utf-8 -*-
# from enum import Enum
from enum import Enum


class ClientTypeEnum(Enum):
    USER_NICKNAME = 100
    USER_EMAIL = 101
    USER_MOBILE = 102

    USER_MINA = 200
    USER_WX = 201


class TagTaskStatusEnum(Enum):
    INACTIVED = 0  # 未开始
    ONGONING = 1  # 进行中
    FINISHED = 2  # 已完成、未审核
    AUDITED_SUCCESS = 3  # 审核成功
    AUDITED_FAILED = 4  # 审核失败
    MODIFY = 5 #修改中


class AuditStatusEnum(Enum):
    SUCCESS = 1  # 审核通过
    FAILED = 0  # 审核不通过


class LabelTaskAuditStatusEnum(Enum):
    SUCCESS = 1  # 审核通过
    FAILED = 0  # 审核不通过


class LabelTaskActiveStatusEnum(Enum):
    FROZEN = 0  # 冻结
    ACTIVATED = 1  # 激活


class TagResultStatusEnum(Enum):
    UNTAGGED = 0  # 未标注
    TAGGED = 1  # 已标注


class UtteranceStatusEnum(Enum):
    PARSED = 0          # 解析了
    SELECTED = 1        # 挑选了
    ASSIGNED_PROJ = 2   # 分配到项目了
    ASSIGNED_TASK = 3   # 分配到任务了
    LABELED = 4         # 标注了


class LabelResultStatusEnum(Enum):
    UNMARKED = 0  # 未标注
    MARKED = 1  # 已标注


class LabelUserMapRelTypeEnum(Enum):
    DEFAULT = 0
    PROJECT = 1
    TASK = 2


class LabelTaskStatusEnum(Enum):
    INACTIVED = 0  # 未开始
    ONGONING = 1  # 进行中
    FINISHED = 2  # 已完成、未审核
    AUDITED_SUCCESS = 3  # 审核成功
    AUDITED_FAILED = 4  # 审核失败
    MODIFY = 5  # 修改中


class ChoicesExItemEnum(Enum):
    ALL = 0     # 全有
    NEITHER = -1   # 全没有


class ChoicesExTypeEnum(Enum):
    TYPE_NOT = 0    # 不扩展
    TYPE_NEITHER = 1   # 扩展全没有
    TYPE_ALL = 2  # 扩展全有
    TYPE_NEITHER_ALL = 3  # 扩展全有


class AsyncReqTypeEnum(Enum):
    DOWNLOAD_SV = 1  # 运维下载
    LOG_PARSER_SV = 2   # 运维解析


class AsyncReqStatusEnum(Enum):
    UNSTARTED = 0
    RUNNING = 1
    SUCCESS = 2
    FAILED = 3


class PrepareTypeEnum(Enum):
    TRAIN_DATA = 1
    TEST_DATA = 2
    ENHANCE_DATA = 3
    LABEL_DATA = 4


class PdataSrcTypeEnum(Enum):
    """ 1:标注，2：识别，3：增强 """
    LABELED_SRC = 1
    RECOGNIZED_SRC = 2
    ENHANCED_SRC = 3


class PrepareStatusEnum(Enum):
    RUNNING = 0
    FINISHED = 1
    FAILED = -1
    DB_DONE = 2
    IDK = 3     # 忘了，爲了保險
