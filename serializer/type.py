#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
@author: Raven
@contact: aducode@126.com
@site: https://github.com/aducode
@file: type.py
@time: 2016/1/31 23:57
"""

import types
import sys
import struct
from datetime import datetime, timedelta

from register import register
from utils import sign, decide


class ProtocolType(object):

    def __init__(self, value=None):
        self.value = value

    @classmethod
    def check(cls, value):
        raise NotImplementedError()

    @classmethod
    def serialize(cls, value, ctx):
        """
        序列化value，并写入ctx
        :param value: 序列化的值
        :param ctx: 上下文
        :return: None
        """
        raise NotImplementedError()

    @classmethod
    def deserialize(cls, ctx):
        """
        反序列化
        :param ctx: 从上下文中读取数据
        :return: 反序列化的对象
        """
        raise NotImplementedError()


class Null(ProtocolType):

    @classmethod
    def check(cls, value):
        return False

    @classmethod
    def serialize(cls, value, ctx):
        ctx.write(struct.pack('<i', 0))

    @classmethod
    def deserialize(cls, ctx):
        return None

"""
**************************** 基本类型 *******************************
"""


class BaseType(ProtocolType):
    pass


class Bool(BaseType):

    @classmethod
    def check(cls, value):
        return isinstance(value, types.BooleanType)

    @classmethod
    def serialize(cls, value, ctx):
        ctx.write(struct.pack('<?', value))

    @classmethod
    def deserialize(cls, ctx):
        (bool_value, ) = struct.unpack('<?', ctx.read(1))
        return bool_value


class Int16(BaseType):

    @classmethod
    def check(cls, value):
        return isinstance(value, types.IntType) and -(2 << 14) <= value <= ((2 << 14) - 1)

    @classmethod
    def serialize(cls, value, ctx):
        ctx.write(struct.pack('<h', value))

    @classmethod
    def deserialize(cls, ctx):
        (int16_value, ) = struct.unpack('<h', ctx.read(2))
        return int16_value


class Int32(BaseType):

    @classmethod
    def check(cls, value):
        return isinstance(value, types.IntType) and -(2 << 30) <= value <= ((2 << 30) - 1)

    @classmethod
    def serialize(cls, value, ctx):
        ctx.write(struct.pack('<i', value))

    @classmethod
    def deserialize(cls, ctx):
        (int32_value, ) = struct.unpack('<i', ctx.read(4))
        return int32_value


class Int64(BaseType):

    @classmethod
    def check(cls, value):
        return isinstance(value, types.IntType) and -(2 << 62) <= value <= ((2 << 62) - 1)

    @classmethod
    def serialize(cls, value, ctx):
        ctx.write(struct.pack('<q', value))

    @classmethod
    def deserialize(cls, ctx):
        (int64_value, ) = struct.unpack('<q', ctx.read(8))
        return int64_value


class Character(BaseType):

    @classmethod
    def check(cls, value):
        return isinstance(value, types.StringType) and len(value) == 1

    @classmethod
    def serialize(cls, value, ctx):
        ctx.write(struct.pack('<s', value))

    @classmethod
    def deserialize(cls, ctx):
        (character_value, ) = struct.unpack('<s', ctx.read(1))
        return character_value


class Byte(BaseType):

    @classmethod
    def check(cls, value):
        return isinstance(value, types.IntType) and -(1 << 7) <= value <= ((1 << 7) - 1)

    @classmethod
    def serialize(cls, value, ctx):
        ctx.write(struct.pack('<b', value))

    @classmethod
    def deserialize(cls, ctx):
        return struct.unpack('<b', ctx.read(1))


class Float(BaseType):

    @classmethod
    def check(cls, value):
        return isinstance(value, types.FloatType)

    @classmethod
    def serialize(cls, value, ctx):
        ctx.write(struct.pack('<f', value))

    @classmethod
    def deserialize(cls, ctx):
        (float_value, ) = struct.unpack('<f', ctx.read(4))
        return float_value


class Double(BaseType):

    @classmethod
    def check(cls, value):
        return isinstance(value, types.FloatType)

    @classmethod
    def serialize(cls, value, ctx):
        ctx.write(struct.pack('<d', value))

    @classmethod
    def deserialize(cls, ctx):
        (double_value, ) = struct.unpack('<d', ctx.read(8))
        return double_value


class Decimal(BaseType):

    @classmethod
    def check(cls, value):
        return isinstance(value, types.IntType)

    @classmethod
    def serialize(cls, value, ctx):
        s = str(value)
        String.serialize(s, ctx)

    @classmethod
    def deserialize(cls, ctx):
        value = String.deserialize(ctx)
        if '.' in value:
            return float(value)
        else:
            return int(value)


class Datetime(BaseType):

    time_zone = 8 * 60 * 60 * 1000

    @classmethod
    def check(cls, value):
        return isinstance(value, datetime)

    @classmethod
    def serialize(cls, value, ctx):
        dl = value - datetime(1970, 1, 1, 0, 0, 0)
        v = int((dl.days * 86400 + dl.seconds) * 1000 + dl.microseconds + cls.time_zone)
        Int64.serialize(value, ctx)

    @classmethod
    def deserialize(cls, ctx):
        timestamp = Int64.deserialize(ctx)
        real_timestamp = timestamp - cls.time_zone
        microseconds = real_timestamp % 1000
        real_timestamp //= 1000
        seconds = real_timestamp % 86400
        days = real_timestamp // 86400
        dl = timedelta(days, seconds, microseconds)
        return datetime(1970, 1, 1, 0, 0, 0) + dl


class String(BaseType):

    @classmethod
    def check(cls, value):
        return isinstance(value, types.StringTypes)

    @classmethod
    def serialize(cls, value, ctx):
        is_ref, hash_code = ctx.is_ref(value)
        length = len(value)
        ctx.write(struct.pack('<?ii', is_ref, hash_code, length))
        if is_ref:
            return
        ctx.write(value)

    @classmethod
    def deserialize(cls, ctx):
        (is_ref, hash_code, ) = struct.unpack('<?i', ctx.read(5))
        if is_ref:
            return ctx.ref(hash_code)
        length = struct.unpack('<i', ctx.read(4))
        obj = ctx.read(length)
        ctx.ref(hash_code, obj)
        return obj

"""
************************************ 容器类型 ****************************
"""


class List(ProtocolType):

    @classmethod
    def check(cls, value):
        return isinstance(value, types.ListType)

    @classmethod
    def serialize(cls, value, ctx):
        type_id = register.get_id(cls)
        is_ref, hash_code = ctx.is_ref(value)
        ctx.write(struct.pack('<i?i', type_id, is_ref, hash_code))
        if is_ref:
            return
        length = len(value)
        ctx.write(struct.pack('<i', length))
        for item in value:
            _item_type, _item = decide(item)
            _item_type_id = register.get_id(_item_type)
            ctx.write(struct.pack('<i', _item_type_id))
            _item_type.serialize(_item, ctx)

    @classmethod
    def deserialize(cls, ctx):
        (type_id, is_ref, hash_code, ) = struct.unpack('<i?i', ctx.read(9))
        if type_id == 0:
            return None
        if is_ref:
            return ctx.ref(hash_code)
        length = struct.pack('<i', ctx.read(4))
        obj = list()
        for i in xrange(length):
            (item_type_id, ) = struct.unpack('<i', ctx.read(4))
            obj.append(register.get(item_type_id).deserialize(ctx))
        ctx.ref(hash_code, obj)
        return obj


class KeyValue(ProtocolType):

    @classmethod
    def check(cls, value):
        return isinstance(value, types.TupleType) and len(value) == 2

    @classmethod
    def serialize(cls, value, ctx):
        type_id = register.get_id(cls)
        is_ref, hash_code = ctx.is_ref(value)
        ctx.write(struct.pack('<i?i', type_id, is_ref, hash_code))
        if is_ref:
            return
        k, v = value
        key_type, k = decide(k)
        key_type_id = register.get_id(key_type)
        ctx.write(struct.pack('<i', key_type_id))
        key_type.serialize(k, ctx)
        value_type, v = decide(v)
        value_type_id = register.get_id(value_type)
        ctx.write(struct.pack('<i', value_type_id))
        value_type.serialize(v, ctx)

    @classmethod
    def deserialize(cls, ctx):
        (type_id, is_ref, hash_code, ) = struct.unpack('<i?i', ctx.read(9))
        if type_id == 0:
            return None
        if is_ref:
            return ctx.ref(hash_code)
        (key_type_id, ) = struct.unpack('<i', ctx.read(4))
        key = register.get(key_type_id).deserialize(ctx)
        (value_type_id, ) = struct.unpack('<i', ctx.read(4))
        value = register.get(value_type_id).deserialize(ctx)
        obj = key, value
        ctx.ref(hash_code, obj)
        return obj


class Array(ProtocolType):

    __generics__ = ProtocolType
    __generics_cache__ = dict()

    @classmethod
    def check(cls, value):
        return isinstance(value, (types.ListType, types.TupleType, bytearray))

    @classmethod
    def serialize(cls, value, ctx):
        _type = cls.__generics__
        type_id = register.get_id(_type)
        is_ref, hash_code = ctx.is_ref(value)
        ctx.write(struct.pack('<i?i', type_id, is_ref, hash_code))
        if is_ref:
            return
        arr = value.value
        length = len(arr)
        ctx.write(struct.pack('<i', length))
        if _type == Byte:
            ctx.write(arr)
        else:
            for item in arr:
                _item_type, _item = decide(item)
                _item_type_id = register.get_id(_item_type)
                ctx.write(struct.pack('<i', _item_type_id))
                _item_type.serialize(_item, ctx)

    @classmethod
    def deserialize(cls, ctx):
        (type_id, is_ref, hash_code, ) = struct.unpack('<i?i', ctx.read(9))
        if type_id == 0:
            return None
        if is_ref:
            return ctx.ref(hash_code)
        length = struct.pack('<i', ctx.read(4))
        _type = register.get(type_id)
        obj = list()
        if issubclass(_type, BaseType):
            # 如果是基本类型（Serializable,容器以外的类型）
            # 则使用_type
            for i in xrange(length):
                obj.append(_type.deserialize(ctx))
        else:
            # 否则使用数据中的type
            for i in xrange(length):
                (item_type_id, ) = struct.unpack('<i', ctx.read(4))
                obj.append(register.get(item_type_id).deserialize(ctx))
        ctx.ref(hash_code, obj)
        return obj


class Map(ProtocolType):

    @classmethod
    def check(cls, value):
        return isinstance(value, types.DictType)

    @classmethod
    def serialize(cls, value, ctx):
        type_id = register.get_id(cls)
        is_ref, hash_code = ctx.is_ref(value)
        ctx.write(struct.pack('<i?i', type_id, is_ref, hash_code))
        if is_ref:
            return
        length = len(value)
        ctx.write(struct.pack('<i', length))
        for k, v in value.items():
            key_type, k = decide(k)
            key_type_id = register.get_id(key_type)
            ctx.write(struct.pack('<i', key_type_id))
            key_type.serialize(k, ctx)
            value_type, v = decide(v)
            value_type_id = register.get_id(value_type)
            ctx.write(struct.pack('<i', value_type_id))
            value_type.serialize(v, ctx)

    @classmethod
    def deserialize(cls, ctx):
        (type_id, is_ref, hash_code, ) = struct.unpack('<i?i', ctx.read(9))
        if type_id == 0:
            return None
        if is_ref:
            return ctx.ref(hash_code)
        length = struct.pack('<i', ctx.read(4))
        _type = register.get(type_id)
        obj = dict()
        for i in xrange(length):
            (key_type_id, ) = struct.unpack('<i', ctx.read(4))
            key_type = register.get(key_type_id)
            key = key_type.deserialize(ctx)
            (value_type_id,) = struct.unpack('<i', ctx.read(4))
            value_type = register.get(value_type_id)
            value = value_type.deserialize(ctx)
            obj[key] = value
        ctx.ref(hash_code, obj)
        return obj


class Set(ProtocolType):

    @classmethod
    def check(cls, value):
        pass

    @classmethod
    def serialize(cls, value, ctx):
        type_id = register.get_id(cls)
        is_ref, hash_code = ctx.is_ref(value)
        ctx.write(struct.pack('<i?i', type_id, is_ref, hash_code))
        if is_ref:
            return
        length = len(value)
        ctx.write(struct.pack('<i', length))
        for item in value:
            _type, _item = decide(item)
            _type_id = register.get_id(_type)
            ctx.write(struct.pack('<i', _type_id))
            _type.serialize(_item, ctx)

    @classmethod
    def deserialize(cls, ctx):
        (type_id, is_ref, hash_code, ) = struct.unpack('<i?i', ctx.read(9))
        if type_id == 0:
            return None
        if is_ref:
            return ctx.ref(hash_code)
        length = struct.pack('<i', ctx.read(4))
        obj = set()
        for i in xrange(length):
            (item_type_id, ) = struct.unpack('<i', ctx.read(4))
            obj.add(register.get(item_type_id).deserialize(ctx))
        ctx.ref(hash_code, obj)
        return obj


"""
********************************** 对象类型 ********************************
"""


class Serializable(ProtocolType):

    @classmethod
    def check(cls, value):
        return isinstance(value, cls)

    @classmethod
    def serialize(cls, value, ctx):
        type_id = register.get_id(cls)
        is_ref, hash_code = ctx.is_ref(value)
        ctx.write(struct.pack('<i?i', type_id, is_ref, hash_code))
        if is_ref:
            return
        # Serializable的子类中记录了属性的序列化类型
        # 所以实例属性不需要像容器类型一样限定成ProtocolType类型
        # 但是如果实例属性是ProtocolType类型，也是允许的
        for desc in cls.__serialize_fields__:
            type_id = register.get_id(desc.type_info.type)
            ctx.write(struct.pack('<i', type_id))
            desc.type_info.type.serialize(decide(getattr(value, desc.name))[1], ctx)

    @classmethod
    def deserialize(cls, ctx):
        (type_id, is_ref, hash_code, ) = struct.unpack('<i?i', ctx.read(9))
        if type_id == 0:
            return None
        if is_ref:
            return ctx.ref(hash_code)
        obj = cls()
        for desc in cls.__serialize_fields__:
            (type_id, ) = struct.unpack('<i', ctx.read(4))
            _type = cls.checked_type(type_id, desc.type_info.type)
            setattr(obj, desc.name, _type.deserialize(ctx))
        ctx.ref(hash_code, obj)
        return obj

    @classmethod
    def checked_type(cls, type_id, type_cls):
        excepted = register.get(type_id)
        real = type_cls
        if not issubclass(excepted, real):
            raise RuntimeError('Excepted type is [{excepted}], but real type is [{real}]'.format(excepted=excepted, real=real))
        return excepted


class Enum(ProtocolType):

    @classmethod
    def check(cls, value):
        """
        有问题
        :param value:
        :return:
        """
        return False

    def serialize(self, ctx):
        pass

    @classmethod
    def deserialize(cls, ctx):
        pass

    @classmethod
    def format(cls, vl):
        for field, value in cls.__dict__.items():
            if not field.startswith('__'):
                if value == vl:
                    return field
        raise RuntimeError('{0} not in Enum'.format(vl))


def enum(**enums):
    check_set = set()
    for k, v in enums.items():
        if k.startswith('__'):
            raise RuntimeError('Key:{0} format error!'.format(k))
        check_set.add(v)
    if len(check_set) != len(enums):
        raise RuntimeError('Multi value!')
    return type('Enum', (Enum, ), enums)


class TypeInfo(object):

    def __init__(self, type=None, value=None, sort_id=sys.maxint):
        if type is None:
            raise RuntimeError('protocol type can not be None')
        if not issubclass(type, ProtocolType):
            raise RuntimeError('{protocol_type} must be the ProtocolType\'s subclass'.format(protocol_type=protocol_type))
        if value is not None and not type.check(value):
            raise RuntimeError(
                    'default value:{default_value} is not {protocol_type} type'.format(
                            default_value=value,
                            protocol_type=type.__name__
                    )
            )
        self.type = type
        self.value = value
        self.sort_id = sort_id

    def __str__(self):
        return 'name={name}, default_value={default_value}, sort_id={sort_id}'.format(
                name=self.type.__name__,
                default_value=self.value,
                sort_id=self.sort_id)


class Descriptor(object):

    def __init__(self, name, type_info):
        self.name = name
        self.type_info = type_info

    def __str__(self):
        return '{name}:'.format(name=self.name) + self.type_info.__str__()

    def __get__(self, instance, owner):
        return self.type_info.value if instance is None else instance.__dict__.get(self.name, self.type_info.value)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value if type(value) != self.type_info.type else value.value

    def __delete__(self, instance):
        del instance.__dict__[self.name]


def member(*args, **kwargs):
    return TypeInfo(*args, **kwargs)


def serializable(*name, **fields):
    if len(name) != 0 and len(name) != 1:
        raise RuntimeError('Invalid entity name!')
    """
    用于class上的注解
    为python类加上类型信息
    :param fields:
    :return:
    """
    def decorator(cls):
        """
        给类加上类型信息
        :param cls:
        :return:
        """
        cls.__serialize_name__ = cls.__name__ if len(name) == 0 else name[0]
        d = dict()
        for field_name, protocol_type in fields.items():
            desc = Descriptor(field_name, protocol_type) if isinstance(protocol_type, TypeInfo) \
                else Descriptor(field_name, TypeInfo(protocol_type))
            d[sign(field_name.lower())] = desc
            setattr(cls, field_name, desc)
        cls.__serialize_fields__ = [item[1] for item in sorted(d.items(), key=lambda x:x[0])]
        register.reg(sign(cls.__serialize_name__), cls)
        return cls

    return decorator


def array(genercis=ProtocolType):
    if not issubclass(genercis, ProtocolType):
        raise RuntimeError('Genercis Type must be subclass of ProtocolType, but found:'+genercis.__str__())
    if genercis == ProtocolType:
        return Array
    if genercis not in Array.__generics_cache__:
        new_cls = type('{name}Array'.format(name=genercis.__name__), (Array, ), {
            '__genercis__': genercis
        })
        Array.__generics_cache__[genercis] = new_cls
    return Array.__generics_cache__[genercis]

register.reg(0, 1, Null)
register.reg(3, Bool)
register.reg(4, Character)
register.reg(5, 6, Byte)
register.reg(7, 8, Int16)
register.reg(9, 10, Int32)
register.reg(11, 12, Int64)
register.reg(13, Float)
register.reg(14, Double)
register.reg(15, Decimal)
register.reg(16, Datetime)
register.reg(18, String)
register.reg(19, 20, 21, List)
register.reg(22, KeyValue)
register.reg(23, Array)
register.reg(24, 25, Map)
register.reg(26, Set)