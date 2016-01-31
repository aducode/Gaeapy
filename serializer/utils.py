#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
@author: Raven
@contact: aducode@126.com
@site: https://github.com/aducode
@file: utils.py
@time: 2016/1/31 23:57
"""


def sign(s):
    """
    计算签名
    :param s:
    :return:
    """
    mask = (1 << 32) - 1
    hash1 = hash2 = 5381
    l = len(s)
    i = 0
    while i < l:
        c = ord(s[i])
        hash1 = ((((hash1 << 5) & mask) + hash1) & mask) ^ c
        i += 1
        if i >= l:
            break
        c = ord(s[i])
        hash2 = ((((hash2 << 5) & mask) + hash2) & mask) ^ c
        i += 1
    ret = (hash1 + ((hash2 * 1566083941) & mask)) & mask
    while ret >= (1 << 31):
        ret -= (1 << 32)
    return ret


def decide(value):
    """
    将python类型，映射成序列化类型
    由于python类型与序列化类型可能为多对一关系（如python的int可能为Byte,Int16,Int32,Int64, float可能为Float，Double)
    所以在使用容器（List， KeyValue， Array， Set，Map）时，为了保证序列化后，其他语言正确的反序列化，需要限定为具体序列化类型
    :param value:
    :return ProtocolType子类
    """

    import types
    from datetime import datetime

    from type import ProtocolType
    from type import Serializable
    from type import Array
    from type import String, List, Set, KeyValue, Map
    from type import Null, Bool, Datetime, Int32, Double
    python_type = type(value)
    if issubclass(python_type, Serializable):
        return python_type, value
    elif issubclass(python_type, Array):
        return python_type, value
    elif issubclass(python_type, ProtocolType):
        # 是包装过的，返回类型和包装的值
        return python_type, value.value
    elif python_type == list:
        return List, value
    elif python_type == set:
        return Set, value
    elif python_type == dict:
        return Map, value
    elif python_type == tuple and len(value) == 2:
        return KeyValue, value
    elif python_type == str:
        return String, value
    elif python_type == datetime:
        return Datetime, value
    elif python_type == bool:
        return Bool, value
    elif python_type == types.NoneType:
        return Null, value
    # 以下是默认策略
    elif python_type == int:
        # 默认是int32,舍去溢出部分
        return Int32, value & ((1 << 32) - 1)
    elif python_type == float:
        # 默认double
        return Double, value
    else:
        return None, value

