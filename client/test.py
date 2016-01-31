#!/usr/bin/python
# -*- coding:utf-8 -*-
from serializer import serializable, member
from serializer import Int32, String, Serializable, Array
from protocol.protocol import ResponseProtocol


def hash_code(s):
    hash2 = hash1 = 5381
    l = len(s)
    i = 0
    while i<l:
        c = ord(s[i])
        tmp1 = (hash1<<5)
        tmp1 = tmp1 & 0xFFFFFFFF
        tmp2 = (tmp1 + hash1)
        tmp2 = tmp2 & 0xFFFFFFFF
        hash1 = tmp2 ^ c
        # hash1 = (0xFFFFFFFF & (0xFFFFFFFF & (hash1 << 5) + hash1)) ^ c
        i += 1
        if i>= l:
            break
        c = ord(s[i])
        tmp1 = (hash2 << 5)
        tmp1 = tmp1 & 0xFFFFFFFF
        tmp2 = hash2 + tmp1
        tmp2 = tmp2 & 0xFFFFFFFF
        hash2 = tmp2 ^ c
        # hash2 = (0xFFFFFFFF & (0xFFFFFFFF & (hash2 << 5) + hash2)) ^ c
        i += 1
    return 0xFFFFFFFF & (hash1 + (0xFFFFFFFF & (0xFFFFFFFF & (hash2 * 1566083941))))


def t1(**fields):
    def _t(cls):
        def __t(*args, **kwargs):
            # for f, t in fields.items():
            #     setattr(cls, f, t)
            obj = cls(*args, **kwargs)
            obj.test='fuck'
            return obj
        return __t
    return _t


def t(**fields):
    def _t(cls):
        for f, tp in fields.items():
            print f, '=', tp
            setattr(cls, f, tp)
        return cls
    return _t


@serializable('TT', age=Int32, name=member(String, 'fuck'))
class TT(Serializable):
    def __init__(self, a, b):
        self.age = a
        self.name = b


@serializable(
        'Fuck',
        e=member(type=TT, value=TT(12, 'ab')),
        info=member(type=String, value="abc"),
)
class TTT(Serializable):pass

if __name__ == '__main__':
    Int32_Array = Array(Int32)
    A = Array(Array(Int32))
    ia = Int32_Array([2, 4, 6])
    ib = Array([1, 2, 3])
    print ia, ib
    print A, Int32_Array
    print ResponseProtocol(None, None)
