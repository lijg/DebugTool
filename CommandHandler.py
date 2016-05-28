#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from time import sleep
from queue import Queue
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from yapsy.PluginManager import PluginManager
from categories import DPlugin
import TextFormatter


class HandlerManager(QThread):

    # 返回命令执行结果
    # int:  0  -- 返回PlainText
    #       1  -- 返回RichText
    # str:  结果
    outSignal = pyqtSignal(int, str)

    def __init__(self):
        super(HandlerManager, self).__init__()

        # 创建工作队列，用户输入的命令按照顺序put进该队列
        # 由CommandHandler在后台逐个处理
        self.workQueue = Queue()

        # 初始化插件功能
        self.initPlugin()

    def __del__(self):
        self.wait()

    def initPlugin(self):
        '''
        启动插件管理器，获取插件列表
        '''

        # 创建插件管理器
        self.pluginManager = PluginManager()

        # 设置插件接口为 DPlugin，所有插件必须继承categories.DPlugin
        self.pluginManager.setCategoriesFilter({"DPlugin": DPlugin})

        # 设置插件目录
        self.pluginManager.setPluginPlaces(['plugins'])

        # 加载插件到内存
        self.pluginManager.locatePlugins()
        self.pluginManager.loadPlugins()

    def getAllPlugins(self):
        '''获取插件列表'''
        return self.pluginManager.getPluginsOfCategory('DPlugin')

    def activateAllPlugins(self):
        '''使能所有插件'''
        for plugin in self.pluginManager.getPluginsOfCategory('DPlugin'):
            plugin.plugin_object.activate()

    def deactivateAllPlugins(self):
        '''禁用所有插件'''
        for plugin in self.pluginManager.getPluginsOfCategory('DPlugin'):
            plugin.plugin_object.deactivate()

    def activatePlugin(self, name):
        '''使能特定插件'''
        self.pluginManager.activatePluginByName(name, category="DPlugin")

    def deactivatePlugin(self, name):
        '''使能特定插件'''
        self.pluginManager.deactivatePluginByName(name, category="DPlugin")

    def processInput(self, userInput):
        '''将命令放入队列'''
        self.workQueue.put((False, userInput))

    def processFile(self, filepath):
        '''将待处理文件放入队列'''
        self.workQueue.put((True, filepath))

    def run(self):
        '''不断从Queue中获取数据，然后执行解析命令'''
        while True:
            isFile, userInput = self.workQueue.get()
            if isFile:
                self.execFile(userInput)
            else:
                self.execCommand(userInput, None)

    def execCommand(self, userInput, currentFile):
        '''
        解析命令
        '''
        if not len(userInput) or userInput.startswith('#'):
            return

        # 命令回显
        self.writeCommand(userInput)

        # 命令分割
        command, *params = userInput.split(maxsplit=1)

        if command == 'source':
            if len(params) == 1:
                filepath = params[0]
                if not os.path.isabs(filepath):
                    basepath = os.path.dirname(currentFile)
                    filepath = os.path.normpath(filepath)
                    filepath = os.path.join(basepath, filepath)
                self.execFile(filepath)
            else:
                self.writeStderr('syntax error: ' + userInput)
        else:
            self.dispatchCommand(userInput)

    def execFile(self, filepath):
        self.writeCommand('Processing file ' + filepath)
        if os.path.isfile(filepath) and os.access(filepath, os.R_OK):
            with open(filepath, 'r') as f:
                for line in f.readlines():
                    line = line.strip()
                    self.execCommand(line, filepath)
        else:
            self.writeStderr('Cannot open file: ' + filepath)

    def dispatchCommand(self, userInput):
        '''将命令分发给各个插件'''

        status = DPlugin.EXEC_NOTFOUND

        for plugin in self.pluginManager.getPluginsOfCategory('DPlugin'):
            ret, resultText = plugin.plugin_object.execCommand(userInput)

            if ret == DPlugin.EXEC_SUCCESS:
                self.writeStdout(resultText)
                status = DPlugin.EXEC_SUCCESS
            elif ret == DPlugin.EXEC_FAILED:
                self.writeStderr(resultText)
                status = DPlugin.EXEC_FAILED

        if status == DPlugin.EXEC_NOTFOUND:
            self.writeStderr(userInput + ': Command not found')

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
