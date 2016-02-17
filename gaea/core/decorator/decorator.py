#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
@author: Raven
@contact: aducode@126.com
@site: https://github.com/aducode
@file: decorator.py
@time: 2016/2/1 0:09
"""


def service(name=None):
    """
    class的装饰器，用来指定service名（默认为类名）
    :param name:
    :return:
    """
    def deco(cls):
        cls.__service_name__ = name if name is not None else cls.__name__
        return cls
    return deco


def operation(name=None, args=tuple(), ret=None):
    """
    由于其他语言不支持kwargs参数，为了保持一致，这里也禁止使用
    :param name:
    :param args:
    :param kwargs:
    :param ret:
    :return:
    """
    def deco(method):
        method.__method_name__ = name if name is not None else method.__name__
        method.__ret__ = ret
        method.__args__ = args if isinstance(args, tuple) else (args, )
        return method
    return deco
