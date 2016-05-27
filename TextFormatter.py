#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
根据不同的输出类型，将文字按照RichText格式输出

作者: lijg
日期: 2016-05-25
'''

def fCommand(text):
    '''
    用户输入，蓝色加粗，加换行
    '''
    return ('<font color="blue"><b>&gt; {}</b></font>'.format(text) +
            '<br />')

def fStderr(text):
    '''
    错误显示，红色加粗，换两行
    '''
    return ('<font color="red"><b>{}</b></font>'.format(text) +
            '<br /><br />')

def fStdout(text):
    '''
    正常显示，加换行
    '''
    return (text + '\n')