# -*- coding: utf-8 -*-
from enum import Enum


class EnhanceTypeEnum(Enum):
    REDUCE_NOISE = 1
    ADD_NOISE = 2
    ADJUST_VOLUME = 3
    VOICE_CONVERSION = 4


# if __name__ == '__main__':
#     a = [e.value for e in EnhanceTypeEnum]
#     a = [e.name for e in EnhanceTypeEnum]
#     print a
