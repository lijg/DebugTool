#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
DebugTool Plugin -- FPGA Debug Handler

Author: lijg
Date: 2016-05-25
'''

from categories import DPlugin

class FPGADebugHandler(DPlugin):
    name = "FPGA Debug Handler"

    def execCommand(self, commandText):
        if self.activate_status:
            command, *params = commandText.split(maxsplit=1)
            if command == 'read_fpga':
                result = [0x1, 0x2, 0x3, 0x4, 0x5]
                return (DPlugin.EXEC_SUCCESS, " ".join(map(str, result)))
            elif command == 'write_fpga':
                return (DPlugin.EXEC_SUCCESS, "write fpga success")
            else:
                return (DPlugin.EXEC_NOTFOUND, '')
        else:
            return super().execCommand(commandText)