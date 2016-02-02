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


def recv(conn):
    data = ''
    while True:
        conn.recv(1024)


def invoker(proxy, func):

    def _func(*args):

        request = RequestProtocol()
        request.lookup = proxy.implement.__class__.__service_name__
        request.methodName = func.__method_name__
        request.paraKVList = [KeyValuePair(_type.__name__, value)
                              for _type, value in zip(func.__args__, args)]
        protocol = Protocol(msg=request,
                            msg_type=MsgType.Request,
                            compress_type=proxy.compress,
                            serialize_type=proxy.serialize,
                            platform=Platform.Java)

        client = socket(AF_INET, SOCK_STREAM)
        client.connect(proxy.address)
        client.send(protocol.to_bytes())



        print '-'*10
        print request.lookup
        print request.methodName
        print [str(kv) for kv in request.paraKVList]
        res = func(*args)
        return res

    return _func
