#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
@author: Raven
@contact: aducode@126.com
@site: https://github.com/aducode
@file: exception
@time: 2016/2/17 17:44
"""


class InternalServerException(Exception):
    """
    服务器端异常
    """
    def __init__(self, error_code, to_ip, from_ip, msg):
        self.error_code = error_code
        self.service_ip = from_ip
        self.client_ip = to_ip
        self.msg = msg

    def __str__(self):
        return '<{service}=>{client}>ERROR:{code} {msg}'.format(service=self.service_ip, client=self.client_ip,
                                                                code=self.error_code, msg=self.msg)