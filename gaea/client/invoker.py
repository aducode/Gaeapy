#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
@author: Raven
@contact: aducode@126.com
@site: https://github.com/aducode
@file: invoker.py
@time: 2016/2/1 23:05
"""

from socket import socket, AF_INET, SOCK_STREAM

from gaea.core.protocol.protocol import MsgType, Platform
from gaea.core.protocol.protocol import Protocol, RequestProtocol, KeyValuePair, Out

from gaea.core.exception import InternalServerException


def recv_data(conn, buf_size=1024):

    _data = ''
    while True:
        _in_buf = conn.recv(buf_size)
        _data += _in_buf if _in_buf else ''
        if (len(_in_buf) if _in_buf else 0) < buf_size:
            break
    conn.close()
    return _data


def invoker(proxy, func):

    def _func(*args):

        type_and_values = zip(func.__args__, args)
        params = list()
        out_params = list()
        for t, v in type_and_values:
            if isinstance(t, Out):
                if not isinstance(v, Out):
                    raise RuntimeError('Value must be Out instance!')
                else:
                    out_params.append(v)
                    params.append((t.value, v.value, ))
            else:
                params.append((t, v, ))
        request = RequestProtocol()
        request.lookup = proxy.implement.__class__.__service_name__
        request.methodName = func.__method_name__
        request.paraKVList = [KeyValuePair(_type.__simple_name__, value)
                              for _type, value in params]
        send_protocol = Protocol(msg=request,
                                 msg_type=MsgType.Request,
                                 compress_type=proxy.compress,
                                 serialize_type=proxy.serialize,
                                 platform=Platform.Java)
        serialized = send_protocol.to_bytes()
        conn = socket(AF_INET, SOCK_STREAM)
        conn.connect(proxy.address)
        conn.send(serialized)
        data = recv_data(conn)
        receive_protocol = Protocol.from_bytes(data)
        if receive_protocol.msg_type == MsgType.Response:
            response = receive_protocol.msg
            response_out_params = response.outpara if response.outpara is not None else list()
            if len(response_out_params) != len(out_params):
                raise RuntimeError('Out parameter num not equal!')
            for i in xrange(len(out_params)):
                out_params[i].value = response_out_params[i]
            return response.result
        elif receive_protocol.msg_type == MsgType.Exception:
            exception = receive_protocol.msg
            exp = InternalServerException(exception.errorCode, exception.toIP, exception.fromIP, exception.errorMsg)
            raise exp

    return _func
