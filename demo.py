#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
@author: Raven
@contact: aducode@126.com
@site: https://github.com/aducode
@file: demo.py
@time: 2016/2/1 20:21
"""

from gaea.client import proxy
from gaea.core import operation, service
from gaea.core import String, Int, Long, Array
from gaea.core import Serializable, serializable
from gaea.core import Out


@serializable(
    value=Int,
    message=String,
)
class Test(Serializable):

    def __str__(self):
        return 'value={value}, message={message}'.format(value=self.value, message=self.message)


@proxy(('127.0.0.1', 9090))
@service()
class TestService(object):

    @operation(args=(Long, Array(Int), Test, Int, String, Out(Long)), ret=Test)
    def getTest(self, t, int_array, test, i, s, l):
        pass


if __name__ == '__main__':
    test_service = TestService()
    t1 = Test()
    t1.value = 100
    t1.message = "hello"
    outpara = Out(1000)
    t2 = test_service.getTest(Long(1), Array(Int)([1, 2, 3]), t1, 111, "world", outpara)
    print t2, outpara.value
