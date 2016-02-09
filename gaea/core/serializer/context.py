#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
@author: Raven
@contact: aducode@126.com
@site: https://github.com/aducode
@file: context.py
@time: 2016/1/31 23:57
"""


class Context(object):
    """
    一次序列化过程的上下文
    """
    def __init__(self, data='', hash_code=1000):
        self.refs = dict()
        self.hash_code_pool = dict()
        self.data = data
        self.hash_code = hash_code

    def ref(self, hash_code, obj=None):
        if obj is None:
            return self.refs.get(hash_code, None)
        else:
            self.refs[hash_code] = obj
            return obj

    def read(self, size):
        ret, self.data = self.data[:size], self.data[size:]
        return ret

    def write(self, data):
        self.data += data

    def __get_hash_code(self, obj):
        if obj is None:
            return 0
        _id = id(obj)
        if _id not in self.hash_code_pool:
            self.hash_code += 1
            self.hash_code_pool[_id] = self.hash_code
        return self.hash_code_pool[_id]

    def is_ref(self, obj):
        if obj is None:
            return True, 0
        hash_code = self.__get_hash_code(obj)
        if hash_code in self.refs:
            return True, hash_code
        else:
            self.refs[hash_code] = obj
            return False, self.hash_code
