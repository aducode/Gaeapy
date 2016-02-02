#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
@author: Raven
@contact: aducode@126.com
@site: https://github.com/aducode
@file: proxy.py
@time: 2016/2/1 19:47
"""

import types

from protocol.protocol import SerializeType, CompressType
from invoker import invoker


class Proxy(object):
    """
    代理类
    """
    def __init__(self, implement, services, serialize=SerializeType.GAEABinary, compress=CompressType.UnCompress):
        """

        :param implement: 代理的类
        :param services: 服务器地址
        :param serialize: 序列化类型
        :param compress: 压缩方式
        :return: 代理类
        """
        self.implement = implement
        self.services = set(services)
        self.serialize = serialize
        self.compress = compress
        self.__current_address_idx = 0

    @property
    def address(self):
        _address = self.services[self.__current_address_idx]
        self.__current_address_idx = (self.__current_address_idx + 1) % len(self.services)
        return _address

    def __getattr__(self, item):
        if hasattr(self.implement, item):
            attr = getattr(self.implement, item)
            if isinstance(attr, types.MethodType) and hasattr(attr, '__method_name__'):
                return invoker(self, attr)
            else:
                return attr
        else:
            raise AttributeError()


def proxy(services, serialize=SerializeType.GAEABinary, compress=CompressType.UnCompress):

    def deco(cls):

        def wrapped(*args, **kwargs):
            obj = cls(*args, **kwargs)
            return Proxy(obj, services, serialize, compress)
        return wrapped

    return deco
