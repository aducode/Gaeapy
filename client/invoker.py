#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
@author: Raven
@contact: aducode@126.com
@site: https://github.com/aducode
@file: invoker.py
@time: 2016/2/1 23:05
"""


def invoker(func):

    def _func(*args):
        params = args
        print zip(func.__args__, params)
        print func.__ret__
        res = func(*args)
        return res

    return _func
