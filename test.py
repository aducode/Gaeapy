#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
@author: Raven
@contact: aducode@126.com
@site: https://github.com/aducode
@file: test.py
@time: 2016/2/1 20:21
"""

from client import proxy
from decorator import operation, service
from serializer import String


@proxy(('127.0.0.1', 8080))
@service()
class Test(object):

    def __init__(self, value):
        self.value = value

    @operation(name='fuck', args=(String, ), ret=String)
    def say(self, msg):
        print self.value, msg


if __name__ == '__main__':
    t=Test(1)
    t.say('fuck')