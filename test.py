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
from serializer import String, Int32, Array
from serializer import Serializable, serializable

@serializable(
    value=Int32,
    message=String,
)
class Test(Serializable):
    pass


@proxy(('127.0.0.1', 9090))
@service()
class TestService(object):

    @operation(args=(Array(Int32), Test, Int32, String), ret=Test)
    def getTest(self, int_array, test, i, s):
        pass

if __name__ == '__main__':
    test_service = TestService()
    t1 = Test()
    t1.value = 100
    t1.message = "hello"
    t2 = test_service.getTest(Array(Int32)([1, 2, 3]), t1, 111, "world")
    print t2