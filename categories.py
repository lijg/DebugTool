#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
DebugTool 插件接口


作者: lijg
日期: 2016-05-25
'''

from yapsy.IPlugin import IPlugin


class DPlugin(IPlugin):
    """Plugins of this class handle the command from user input or file"""

    # 返回值类型
    EXEC_NOTFOUND = 0
    EXEC_SUCCESS = 1
    EXEC_FAILED = 2

    name = "No Handler"
    activate_status = False

    def activate(self):
        self.activate_status = True

    def deactivate(self):
        self.activate_status = False

    def isActivate(self):
        return self.activate_status

    def execCommand(self, command):
        """Takes command, returns status and execute result"""
        return (self.EXEC_NOTFOUND, '')
