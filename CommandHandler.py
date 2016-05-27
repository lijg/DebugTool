#!/usr/bin/python
# -*- coding: utf-8 -*-

from time import sleep
from queue import Queue
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import TextFormatter

ESYNTAX = 60


CMD_RD_FPGA_REG = 'rd_fpga_reg'
CMD_RD_FPGA_MEM = 'rd_fpga_mem'
CMD_WR_FPGA_REG = 'wr_fpga_reg'
CMD_WR_FPGA_MEM = 'wr_fpga_mem'


VALID_CMDS = [
'rd_fpga_reg',
'rd_fpga_mem',
'wr_fpga_reg',
'wr_fpga_mem'
]

HELP_STRING = '''help                        帮助
clear                       清屏
exit                        退出 
rd_fpga_reg addr            读FPGA寄存器
rd_fpga_mem addr length     读FPGA内存空间
wr_fpga_reg addr val        写FPGA积存器
wr_fpga_mem addr mem.bin    写FPGA内存空间
'''


class Handler(QThread):

    # 返回命令执行结果
    # int:  0  -- 返回PlainText
    #       1  -- 返回RichText
    # str:  结果
    outSignal = pyqtSignal(int, str)

    def __init__(self):
        super(Handler,self).__init__() 

        # 创建命令队列，用户输入的命令按照顺序put进该队列
        # 由CommandHandler在后台逐个处理
        self.userInputQueue = Queue()

    def __del__(self):
        self.wait()

    def process(self, userInput):
        '''
        将命令放入队列
        '''
        self.userInputQueue.put(userInput)

    def writeCommand(self, text):
        '''
        输出原始命令，蓝色加粗显示，以示区分
        '''
        self.outSignal.emit(1, text)

    def writeStdout(self, text):
        '''
        返回普通输出，文本后加换行
        '''
        self.outSignal.emit(0, text)

    def writeStderr(self, text):
        '''
        返回错误输出，红色加粗显示，以示区分
        '''
        self.outSignal.emit(2, text)

    def run(self):
        '''
        不断从Queue中获取数据，然后执行解析命令
        '''
        while 1:
            userInput = self.userInputQueue.get()
            self.parser(userInput)  

    def parser(self, userInput):
        # pass
        
        '''
        解析命令
        '''
        self.writeCommand(userInput)
        cmd = userInput.split()[0]
        # sleep(1)
        if cmd == 'help':
            self.writeStdout(HELP_STRING)
        else:
            self.writeStderr(userInput + ': Command not found')

    # def IsInt(self, s):
    #     try:
    #         ret = int(s, 0)
    #         return True, ret
    #     except ValueError:
    #         return False, 0

    # def ReadOneBin(self, filepath):
    #     try:
    #         with open(filepath, 'rb') as f:
    #             val = struct.unpack('I', f.read(4))[0]
    #     except IOError:
    #         print 'Error! Cannot Open "' + filepath + '"'
    #         return -EFILE
    #     finally:
    #         return val

    # def execute(self, command, *args):
    #     if command == CMD_WR_FPGA_REG:

    #         if len(args) != 2:
    #             print 'Error! ' + CMD_WR_FPGA_REG + ' syntax error!'
    #             return -ESYNTAX

    #         addr = int(args[0], 0)
    #         ret, val = self.IsInt(args[1])
    #         if not ret:
    #             val = self.ReadOneBin(args[1])

    #         print 'write %08X: %08X\n' % (addr, val)
    #         self.server.wr_fpga_reg(addr, val)

    #     elif command == CMD_RD_FPGA_REG:
    #         if len(args) != 1:
    #             print 'Error! ' + CMD_RD_FPGA_REG + ' syntax error!'
    #             return -ESYNTAX

    #         addr = int(args[0], 0)

    #         print 'read %08X: %08X\n' % (addr, self.server.rd_fpga_reg(addr))
            
