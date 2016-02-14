#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
@author: Raven
@contact: aducode@126.com
@site: https://github.com/aducode
@file: protocol.py
@time: 2016/1/31 23:57
"""

import struct
from ..serializer.context import Context
from ..serializer.type import enum
from ..serializer.type import Serializable, serializable
from ..serializer.type import Any, String, List, array, Int32

MsgType = enum(
        Response=1,
        Request=2,
        Exception=3,
        Config=4,
        Handclasp=5,
        Reset=6
)

CompressType = enum(
        UnCompress=0,
        SevenZip=1,
        DES=2
)

SerializeType = enum(
        JSON=1,
        JavaBinary=2,
        XML=3,
        GAEABinary=4
)

Platform = enum(
        Dotnet=0,
        Java=1,
        C=2,
        Python=3
)


class Protocol(object):

    magic = (9, 11, 13, 17, 18)

    def __init__(self, session_id=0, service_id=0,
                 msg=None, msg_len=None, msg_type=None,
                 compress_type=CompressType.UnCompress,
                 serialize_type=SerializeType.GAEABinary,
                 platform=Platform.Python,
                 version=1):
        self.msg = msg
        self.msg_len = msg_len
        self.session_id = session_id
        self.service_id = service_id
        self.version = version
        self.compress_type = compress_type
        self.serialize_type = serialize_type
        self.platform = platform
        self.msg_type = get_msg_type(self.msg) if self.msg else msg_type

    def __str__(self):
        return 'version={version}, ' \
               'msg_len={msg_len}, ' \
               'session_id={session_id}, ' \
               'service_id={service_id}, ' \
               'msg_type={msg_type}, ' \
               'compress_type={compress_type}, ' \
               'serialize_type={serialize_type}, ' \
               'platform={platform}'.format(
                version=self.version,
                msg_len=self.msg_len,
                session_id=self.session_id,
                service_id=self.service_id,
                msg_type=MsgType.format(self.msg_type),
                compress_type=CompressType.format(self.compress_type),
                serialize_type=SerializeType.format(self.serialize_type),
                platform=Platform.format(self.platform))

    def to_bytes(self):
        ctx = Context()
        self.msg.__class__.serialize(self.msg, ctx)
        msg_data = ctx.data
        self.msg_len = len(msg_data)
        return struct.pack('<biibbbbb',
                           self.version,
                           self.msg_len,
                           self.session_id,
                           self.service_id,
                           self.msg_type,
                           self.compress_type,
                           self.serialize_type,
                           self.platform) + msg_data + struct.pack('<bbbbb', *self.magic)

    @classmethod
    def from_bytes(cls, data):
        data, magic_data = data[:-5], data[-5:]
        _magic = struct.unpack('<bbbbb', magic_data)
        assert(_magic == cls.magic)
        (
            version,
            msg_len,
            session_id,
            service_id,
            msg_type,
            compress_type,
            serialize_type,
            platform
        ) = struct.unpack('<biibbbbb', data[:14])
        ret = cls(version=version,
                  msg_len=msg_len,
                  session_id=session_id,
                  msg_type=msg_type,
                  compress_type=compress_type,
                  serialize_type=serialize_type,
                  platform=platform)
        ret.msg = msg(ret.msg_type).deserialize(Context(data[14:]))
        return ret


def get_msg_type(msg):
    if isinstance(msg, ResponseProtocol):
        return MsgType.Response
    elif isinstance(msg, RequestProtocol):
        return MsgType.Request
    elif isinstance(msg, ExceptionProtocol):
        return MsgType.Exception
    elif isinstance(msg, ConfigProtocol):
        return MsgType.Config
    elif isinstance(msg, HandclaspProtocol):
        return MsgType.Handclasp
    elif isinstance(msg, ResetProtocol):
        return MsgType.Reset
    else:
        return None


@serializable(
    result=Any,
    outpara=array(Any),
)
class ResponseProtocol(Serializable):
    pass


@serializable(
    lookup=String,
    methodName=String,
    paraKVList=List,
)
class RequestProtocol(Serializable):
    pass


@serializable(
    errorCode=Int32,
    toIP=String,
    fromIP=String,
    errorMsg=String,
)
class ExceptionProtocol(Serializable):
    pass


@serializable(

)
class ConfigProtocol(Serializable):
    pass


@serializable(
    type=String,
    data=String,
)
class HandclaspProtocol(Serializable):
    pass


@serializable(
    msg=String,
)
class ResetProtocol(Serializable):
    pass


class Out(object):
    """
    输出参数，不参与序列化
    """
    def __init__(self, value=None):
        self.value = value


@serializable(
    'RpParameter',
    name=String,
    value=Any,
)
class KeyValuePair(Serializable):

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return 'name={name}, value={value}'.format(name=self.name, value=self.value)


__MSG_MAP__ = {
    MsgType.Response: ResponseProtocol,
    MsgType.Request: RequestProtocol,
    MsgType.Exception: ExceptionProtocol,
    MsgType.Config: ConfigProtocol,
    MsgType.Handclasp: HandclaspProtocol,
    MsgType.Reset: ResetProtocol,
}


def msg(msg_type):
    return __MSG_MAP__.get(msg_type, None)


