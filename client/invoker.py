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

from protocol.protocol import MsgType, Platform
from protocol.protocol import Protocol, RequestProtocol, KeyValuePair


def recv_data(conn, buf_size=1024):

    _data = ''
    while True:
        _in_buf = conn.recv(buf_size)
        _data += _in_buf if _in_buf else ''
        if (len(_in_buf) if _in_buf else 0) < buf_size:
            break
    return _data


def invoker(proxy, func):

    def _func(*args):

        request = RequestProtocol()
        request.lookup = proxy.implement.__class__.__service_name__
        request.methodName = func.__method_name__
        request.paraKVList = [KeyValuePair(_type.__simple_name__, value)
                              for _type, value in zip(func.__args__, args)]
        send_protocol = Protocol(msg=request,
                            msg_type=MsgType.Request,
                            compress_type=proxy.compress,
                            serialize_type=proxy.serialize,
                            platform=Platform.Java)

        conn = socket(AF_INET, SOCK_STREAM)
        conn.connect(proxy.address)
        serialized = send_protocol.to_bytes()
        conn.send(serialized)
        data = recv_data(conn)
        receive_protocol = Protocol.from_bytes(data)
        assert(receive_protocol.msg_type == MsgType.Response)
        response = receive_protocol.msg
        # res = func(*args)
        return response.result

    return _func
