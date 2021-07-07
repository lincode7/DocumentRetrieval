# -*- coding: utf-8 -*-
'''
PyQt QComboBox和QSpinBox禁止鼠标滚动
对包含这2中控件的滚动区域的优化
'''
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QComboBox, QSpinBox





class CustomQSB(QSpinBox):
    def wheelEvent(self, e):
        if e.type() == QEvent.Wheel:
            e.ignore()
