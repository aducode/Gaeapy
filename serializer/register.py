#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
@author: Raven
@contact: aducode@126.com
@site: https://github.com/aducode
@file: register
@time: 2016/2/1 0:15
"""


class ProtocolTypeRegister(object):

    def __init__(self):
        self.__registed_types__ = dict()
        self.__registed_type_id__ = dict()

    def reg(self, *args):
        if len(args) < 2:
            raise RuntimeError()
        value = args[-1]
        keys = args[:-1]
        for key in keys:
            self.__registed_types__[key] = value
        self.__registed_type_id__[value] = keys[0]

    def get(self, key):
        return self.__registed_types__.get(key, None)

    def get_id(self, t):
        return self.__registed_type_id__.get(t, None)


register = ProtocolTypeRegister()
