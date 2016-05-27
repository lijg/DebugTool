#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
DebugTool Plugin -- ARM Debug Handler

Author: lijg
Date: 2016-05-25
'''

from categories import DPlugin

class FPGADebugHandler(DPlugin):
    name = "ARM Debug Handler"

    def execCommand(self, commandText):
        if self.activate_status:
            command, *params = commandText.split(maxsplit=1)
            if command == 'read_arm':
                result = [0x1, 0x2, 0x3, 0x4, 0x5]
                return (DPlugin.EXEC_SUCCESS, " ".join(map(str, result)))
            elif command == 'write_arm':
                return (DPlugin.EXEC_SUCCESS, "write arm success")
            else:
                return (DPlugin.EXEC_NOTFOUND, '')
        else:
            return super().execCommand(commandText)