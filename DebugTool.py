#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
DebugTool 通用调试工具界面

通用调试工具主界面程序，基于PyQt5

作者: lijg
日期: 2016-05-25
'''

import os
import functools
import sys
from PyQt5.QtCore import Qt, QTextCodec
from PyQt5.QtWidgets import (
    QWidget,
    QMainWindow,
    QApplication,
    QAction,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QFileDialog)
from PyQt5.QtGui import QTextCursor, QIcon

# 命令由CommandHandler处理
from CommandHandler import HandlerManager

import TextFormatter

# 默认窗口大小800x600
WDW_WIDTH = 800
WDW_HEIGHT = 600


# 历史命令数据文件
HISTORY_FILE = '.history'

# 基础命令两个，退出程序和清屏
# 其他用户命令由CommandHandler处理
CMD_EXIT = 'exit'
CMD_CLEAR = 'clear'
CMD_HELP = 'help'
CMD_COMMENT = '#'


def resource_path(rel_path):
    '''
    工具栏ICON资源路径

    以Python脚本运行时，这些文件在当前目录下；
    编译成EXE文件时，这些文件通过pyinstaller打包，在sys._MEIPASS目录下
    '''
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, rel_path)


class CmdLineEdit(QLineEdit):
    '''
    自定义的命令输入框，基于QLineEdit，增加了记录命令功能。

    类似于Linux终端，可以通过上下箭头选择历史命令
    '''

    def __init__(self, parent):
        super().__init__(parent)

        # 记录历史命令
        self.history = []
        self.histidx = 0

    def keyPressEvent(self, e):
        '''
        重载按键事件，当按上下箭头时，选择历史命令
        '''
        if e.key() == Qt.Key_Up:
            self.useHistory(-1)
        elif e.key() == Qt.Key_Down:
            self.useHistory(1)
        else:
            super().keyPressEvent(e)

    def useHistory(self, delta):
        '''
        使用历史命令填充lineEdit

        delta代表偏移量
        '''

        if delta < 0 and self.histidx == 0:
            return

        if delta > 0 and len(self.history) <= self.histidx + delta:
            self.histidx = len(self.history)
            self.clear()
            return

        self.histidx += delta
        htext = self.history[self.histidx]
        self.setText(htext)

    def addHistory(self, histcmd):
        '''
        添加历史记录，如果当前命令与记录中上一条命令一样，则不记录
        '''
        if histcmd:
            if len(self.history) == 0 or self.history[-1] != histcmd:
                self.history.append(histcmd)
                self.histidx = len(self.history)

    def loadHistory(self, filename):
        '''
        从文件加载历史命令，每行一条，最大只加载1000行
        '''
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                hist = f.readlines()[-1000:]
                self.history = [x.strip() for x in hist]
                self.histidx = len(self.history)

    def saveHistory(self, filename):
        # 将历史命令存入文件中，只存1000条
        histbuf = '\n'.join(self.history[-1000:])
        with open(filename, 'w') as f:
            f.write(histbuf)


class DebugTool(QMainWindow):
    '''
    含有状态栏的窗口
    '''

    def __init__(self):
        super().__init__()

        # 创建CommandHandler
        self.handler = HandlerManager()

        # CommandHandler的输出结果通过outSignal信号返回给DebugTool
        self.handler.outSignal.connect(self.writeOutput)

        # 启动CommandHandler的后台线程
        self.handler.start()

        self.initUI()

        # QTextCodec.setCodecForCStrings(QTextCodec.codecForName("UTF-8"))

    def initMenuAndToolbar(self):
        '''
        初始化菜单和工具栏

        菜单：
            File
                -- Open File
                -- 分隔符
                -- Exit
            Command
                -- SendFile

        工具栏：
            |Connect | SendFile

        '''

        # 打开文件
        iconpath = resource_path('openfile.png')
        sendAction = QAction(QIcon(iconpath), 'OpenFile', self)
        sendAction.triggered.connect(self.onOpenFile)

        # 退出
        iconpath = resource_path('exit.png')
        exitAction = QAction(QIcon(iconpath), 'Exit', self)
        exitAction.triggered.connect(self.close)

        iconpath = resource_path('help.png')
        helpAction = QAction(QIcon(iconpath), 'Help', self)
        helpAction.triggered.connect(self.onHelp)

        # 使能所有插件
        iconpath = resource_path('activate.png')
        activateAllAction = QAction(QIcon(iconpath), 'ActivateAll', self)
        activateAllAction.triggered.connect(self.onActivateAll)

        # 禁用所有插件
        iconpath = resource_path('deactivate.png')
        deactivateAllAction = QAction(QIcon(iconpath), 'DeactivateAll', self)
        deactivateAllAction.triggered.connect(self.onDeactivateAll)

        # File菜单
        fileMenu = self.menuBar().addMenu('&File')
        fileMenu.addAction(sendAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)

        # Plugin菜单
        pluginMenu = self.menuBar().addMenu('&Plugin')
        pluginMenu.addAction(activateAllAction)
        pluginMenu.addAction(deactivateAllAction)
        pluginMenu.addSeparator()

        for plugin in self.handler.getAllPlugins():
            pluginSubMenu = pluginMenu.addMenu(plugin.plugin_object.name)

            iconpath = resource_path('activate.png')
            pluginActivateAction = QAction(QIcon(iconpath), "Activate", self)
            pluginActivateAction.triggered.connect(functools.partial(
                self.onPluginClicked, plugin.plugin_object.name, True))

            iconpath = resource_path('deactivate.png')
            pluginDeactivateAction = QAction(
                QIcon(iconpath), "Deactivate", self)
            pluginDeactivateAction.triggered.connect(functools.partial(
                self.onPluginClicked, plugin.plugin_object.name, False))

            pluginSubMenu.addAction(pluginActivateAction)
            pluginSubMenu.addAction(pluginDeactivateAction)

        # About菜单
        aboutMenu = self.menuBar().addMenu('&About')
        aboutMenu.addAction(helpAction)

        # 工具栏
        toolbar = self.addToolBar('MainToolBar')
        toolbar.setMovable(False)
        # toolbar.addAction(connectAction)
        toolbar.addAction(sendAction)
        # toolbar.addAction(helpAction)
        # toolbar.addAction(exitAction)

    def initMainUI(self):
        '''
        初始化主界面，一个TextEdit用来显示输出结果，一个LineEdit用来获取输入命令
        '''

        # 创建一个QWidget来包含其它所有控件
        centerWidget = QWidget(self)

        # CmdLine用来获取用户输入，响应 回车键 按下事件
        self.cmdline = CmdLineEdit(centerWidget)
        self.cmdline.returnPressed.connect(self.onCmdlineRerurnPressed)
        self.cmdline.setFocus()

        # 启动式，从文件加载历史命令
        self.cmdline.loadHistory(HISTORY_FILE)

        # LogOutput用来显示输出结果，只读
        self.logOutput = QTextEdit(centerWidget)
        self.logOutput.setReadOnly(True)
        self.logOutput.setAcceptRichText(True)

        # 用一个垂直Box将logOutput和cmdLine放在一起
        vbox = QVBoxLayout(centerWidget)
        vbox.addWidget(self.logOutput)
        vbox.addWidget(self.cmdline)

        # 设置主界面显示内容
        self.setCentralWidget(centerWidget)

    def initUI(self):
        '''
        初始化界面
        '''

        # 菜单和工具栏
        self.initMenuAndToolbar()

        # 主界面
        self.initMainUI()

        # 设置默认大小
        self.resize(WDW_WIDTH, WDW_HEIGHT)

        # 标题
        self.setWindowTitle('DebugTool')
        # self.show()

    def onConnect(self):
        print('onConnect!')

    def onOpenFile(self):
        '''
        打开窗口，选择命令文件，支持一次选择多个文件
        '''
        filepaths, _ = QFileDialog.getOpenFileNames(
            self, 'Open file', None, 'Command Files (*.cmd);;All Files (*)')

        if filepaths:
            for filepath in filepaths:
                filepath = os.path.normpath(filepath)
                self.handler.processFile(filepath)

    def onHelp(self):
        '''
        打印帮助命令
        '''
        self.processCommand(CMD_HELP)

    def onCmdlineRerurnPressed(self):
        '''
        当用户按下回车键时触发此函数
        获取用户输入，清空cmdline，然后将命令提交给处理函数
        '''
        userInput = str(self.cmdline.text()).strip()
        self.cmdline.clear()
        self.cmdline.addHistory(userInput)

        self.processCommand(userInput)

    def processCommand(self, userInput):
        '''
        判断命令类型，如果是基础命令，如exit和clear等，直接执行;
        否则，发送给CommandHandler执行
        '''
        # 如果时空命令或注释，直接返回
        if not len(userInput) or userInput.startswith(CMD_COMMENT):
            return

        # 获取用户输入的第一个单词作为命令
        command, *params = userInput.split()

        if command == CMD_EXIT:
            self.close()
        elif command == CMD_CLEAR:
            self.logOutput.clear()
        else:
            # 提交给CommandHandler处理
            self.handler.processInput(userInput)

    def writeOutput(self, textType, commandOutput):
        '''
        获取CommandHandler的输出，显示到logOutput

        0   -   普通内容
        1   -   命令输出
        2   -   错误输出
        3   -   自定义RichText
        '''
        if textType == 0:
            self.logOutput.insertPlainText(
                TextFormatter.fStdout(commandOutput))
        elif textType == 1:
            self.logOutput.insertHtml(TextFormatter.fCommand(commandOutput))
        elif textType == 2:
            self.logOutput.insertHtml(TextFormatter.fStderr(commandOutput))
        else:
            self.logOutput.insertHtml(commandOutput)

        # 滚动到最新的内容
        self.logOutput.moveCursor(QTextCursor.End)

    def onDeactivateAll(self):
        self.handler.deactivateAllPlugins()

    def onActivateAll(self):
        self.handler.activateAllPlugins()

    def onPluginClicked(self, name, activate):
        if activate:
            self.handler.activatePlugin(name)
        else:
            self.handler.deactivatePlugin(name)

    def closeEvent(self, event):
        '''
        关闭窗口前，将历史命令数据保存到文件
        '''
        self.cmdline.saveHistory(HISTORY_FILE)
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DebugTool()
    ex.show()
    sys.exit(app.exec_())
