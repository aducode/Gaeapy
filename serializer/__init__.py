#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
@author: Raven
@contact: aducode@126.com
@site: https://github.com/aducode
@file: __init__.py
@time: 2016/1/31 23:57
"""
import types

from type import ProtocolType as _ProtocolType

from type import Null
from type import Bool
from type import Byte
from type import Int16
from type import Int32
from type import Int64
from type import Character
from type import Float
from type import Double
from type import Decimal
from type import Datetime

from type import String

from type import List
from type import Set
from type import Map
from type import KeyValue

from type import array as _array
from type import Array as _Array

from type import enum

from type import Serializable
from type import serializable, member

b = Byte
c = Character
s = i16 = Int16
i = i32 = Int32
l = i64 = Int64
f = Float
d = Double
decimal = Decimal


def Array(para):
    """

    :param para:
    :return:
    """
    if isinstance(para, types.TypeType):
        return _array(para)
    else:
        return _Array(para)
