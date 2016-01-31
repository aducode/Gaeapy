#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
@author: Raven
@contact: aducode@126.com
@site: https://github.com/aducode
@file: client.py
@time: 2016/1/31 23:57
"""

import socket
import struct

from protocol.protocol import Protocol, ResponseProtocol
from serializer.type import Serializable, serializable
from serializer.type import String, Int32


@serializable(
    value=Int32,
    message=String,
)
class Test(Serializable):
    pass


def recv(conn, buf_size=1024):
    _data = ''
    while True:
        _inbuf = conn.recv(buf_size)
        _data += _inbuf if _inbuf else ''
        if (len(_inbuf) if _inbuf else 0) < buf_size:
            break
    return _data


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 16002,))
    s.listen(1)
    while True:
        print 'waiting for client....'
        conn, addr = s.accept()
        print addr
        # 魔数
        magic_data = conn.recv(5)
        magic = struct.unpack('bbbbb', magic_data)
        assert(magic == (18, 17, 13, 10, 9,))
        #消息头
        p = Protocol.from_bytes(recv(conn))
        response = ResponseProtocol()
        """
        #下面是协议体
        # RequestProtocol对象
        type_id = struct.unpack('i', conn.recv(4))
        print 'type_id:', type_id
        is_ref = struct.unpack('b', conn.recv(1))
        print 'is_ref:', is_ref
        hash_code = struct.unpack('i', conn.recv(4))
        print 'hash_code:', hash_code
        # 对象属性
        (type_id, ) = struct.unpack('i', conn.recv(4))
        (type_id2,) = struct.unpack('i', conn.recv(4))
        (is_ref, ) = struct.unpack('b', conn.recv(1))
        (hash_code, ) = struct.unpack('i', conn.recv(4))
        (total_len, ) = struct.unpack('i', conn.recv(4))
        print 'type_id:', type_id
        print 'type_id2:', type_id2
        print 'is_ref:', is_ref
        print 'hash_code:', hash_code
        print 'total_len:', total_len
        print '-'*10
        (type_id, ) = struct.unpack('i', conn.recv(4))
        print 'type_id:', type_id
        (type_id2, ) = struct.unpack('i', conn.recv(4))
        print 'type_id2:', type_id2
        """
