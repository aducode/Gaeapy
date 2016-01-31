#!/usr/bin/python
# -*- coding:utf-8 -*-
import struct
from datetime import datetime, timedelta
import common.type


class Serializer(object):

    def serialize(self, value):
        """
        序列化到string
        :param value:需要序列化的数据
        :return: string 序列化后的数据
        """
        raise NotImplementedError()

    def deserialize(self, data):
        """
        从string反序列化
        :param data: 需要反序列化的数据
        :return:
        """
        raise NotImplementedError()


class NoneSerializer(Serializer):

    def serialize(self, value=0):
        return struct.pack('!i', value)

    def deserialize(self, data):
        return struct.unpack('!i', data)


class ObjectSerializer(Serializer):

    def serialize(self, value):
        pass

    def deserialize(self, data):
        print self.inner_class


class BooleanSerializer(Serializer):

    def serialize(self, value):
        return struct.pack('!?', value)

    def deserialize(self, data):
        return struct.unpack('!?', data)


class CharacterSerializer(Serializer):

    def serialize(self, value):
        return struct.pack('!s', value)

    def deserialize(self, data):
        return struct.unpack('!s', data)


class ByteSerializer(Serializer):

    def serialize(self, value):
        return struct.pack('!b', value)

    def deserialize(self, data):
        return struct.unpack('!b', data)


class Int16Serializer(Serializer):

    def serialize(self, value):
        return struct.pack('!h', value)

    def deserialize(self, data):
        return struct.unpack('!h', data)


class Int32Serializer(Serializer):

    def serialize(self, value):
        return struct.pack('!i', value)

    def deserialize(self, data):
        return struct.unpack('!i', data)


class Int64Serializer(Serializer):

    def serialize(self, value):
        return struct.pack('!q', value)

    def deserialize(self, data):
        return struct.unpack('!q', data)


class FloatSerializer(Serializer):

    def serialize(self, value):
        return struct.pack('!f', value)

    def deserialize(self, data):
        return struct.unpack('!f', data)


class DoubleSerializer(Serializer):

    def serialize(self, value):
        return struct.pack('!d', value)

    def deserialize(self, data):
        return struct.unpack('!d', data)


class DecimalSerializer(Serializer):

    def serialize(self, value):
        return SerializerFactory.get_serializer(StringSerializer).write(value)

    def deserialize(self, data):
        ret = SerializerFactory.get_serializer(StringSerializer).read(data)
        try:
            return int(ret)
        except ValueError:
            return 0


class DateTimeSerializer(Serializer):

    time_zone = 8 * 60 * 60 * 1000

    def serialize(self, value):
        dl = value - datetime(1970, 1, 1, 0, 0, 0)
        return SerializerFactory.get_serializer(Int64Serializer).write(int((dl.days * 86400 + dl.seconds) * 1000 +
                                                                           dl.microseconds + self.time_zone))

    def deserialize(self, data):
        timestamp = SerializerFactory.get_serializer(Int64Serializer).read(data)
        real_timestamp = timestamp - self.time_zone
        microseconds = real_timestamp % 1000
        real_timestamp //= 1000
        seconds = real_timestamp % 86400
        days = real_timestamp // 86400
        dl = timedelta(days, seconds, microseconds)
        return datetime(1970, 1, 1, 0, 0, 0) + dl


class StringSerializer(Serializer):

    def serialize(self, value):
        ref, flag = SerializerFactory.write_ref(value)
        if flag:
            return ref
        l = len(value)
        return struct.pack('!i%ds' % l, l, value) + ref

    def deserialize(self, data):
        (is_ref, ) = struct.unpack(data[0])
        #TODO


class ListSerializer(Serializer):

    def serialize(self, value):
        pass

    def deserialize(self, data):
        pass


class KeyValueSerializer(Serializer):

    def serialize(self, value):
        pass

    def deserialize(self, data):
        pass


class ArraySerializer(Serializer):

    def serialize(self, value):
        pass

    def deserialize(self, data):
        pass


class MapSerializer(Serializer):

    def serialize(self, value):
        pass

    def deserialize(self, data):
        pass


class EnumSerializer(Serializer):

    def serialize(self, value):
        pass

    def deserialize(self, data):
        pass


class SerializerFactory(object):

    noneSerializer = NoneSerializer()
    #objectSerializer = ObjectSerializer()
    booleanSerializer = BooleanSerializer()
    characterSerializer = CharacterSerializer(),
    byteSerializer = ByteSerializer(),
    int16Serializer = Int16Serializer(),
    int32Serializer = Int32Serializer(),
    int64Serializer = Int64Serializer(),
    floatSerializer = FloatSerializer(),
    doubleSerializer = DoubleSerializer(),
    decimalSerializer = DecimalSerializer(),
    dateTimeSerializer = DateTimeSerializer(),
    stringSerializer = StringSerializer(),
    listSerializer = ListSerializer(),
    keyValueSerializer = KeyValueSerializer(),
    arraySerializer = ArraySerializer(),
    mapSerializer = MapSerializer(),
    enumSerializer = EnumSerializer(),
    __serializer_cache__ = dict()

    @classmethod
    def get_serializer(cls, _type):
        if not _type:
            return cls.noneSerializer
        if issubclass(_type, common.type.Enum):
            return cls.enumSerializer

        if _type not in cls.__serializer_cache__:
            cls.__serializer_cache__[_type] = type('{class_name}Serializer'.format(class_name=_type.__name__),
                                                   (ObjectSerializer, ),
                                                   {'inner_class': _type, })()
        return cls.__serializer_cache__[_type]

    _obj_map = dict()
    _current_hash_code = 1000

    @classmethod
    def get_hash_code(cls, obj):
        if not obj:
            return 0
        else:
            if obj in cls._obj_map:
                return cls._obj_map[obj]
            else:
                cls._current_hash_code += 1
                cls._obj_map[obj] = cls._current_hash_code
                return cls._current_hash_code

    _ref_pool = dict()

    @classmethod
    def write_ref(cls, obj):
        if not obj:
            return struct.pack('!bi', 1, 0), True
        hash_code = cls.get_hash_code(obj)
        if hash_code in cls._ref_pool:
            return struct.pack('!bi', 1, hash_code), True
        else:
            cls._ref_pool[hash_code] = obj
            return struct.pack('!bi', 0, hash_code), False
