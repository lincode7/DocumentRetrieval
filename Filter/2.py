# -*- coding: utf-8 -*-
import sys, glob, os

from PyQt5.QtCore import QIODevice, QFile
from PyQt5.QtGui import QFontDatabase, QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.uic import loadUi


class MainApp(QMainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        self.importResource()
        # self.hideWidget()
        # self.actions()
        # self.datainit()

    # 动态加载ui
    def importResource(self):
        ui_path = r'.\resources\ui\untitled.ui'
        img = r'.\resources\img\filter.png'
        fonts = glob.glob(r'.\resources\font\*.ttf')
        # 导入ui
        ui_file = QFile(ui_path)
        if not ui_file.open(QIODevice.ReadOnly):
            print("Cannot open {}: {}".format(ui_path, ui_file.errorString()))
            sys.exit(-1)
        loadUi(ui_file, self)
        ui_file.close()
        # 导入图标
        self.setWindowIcon(QIcon(img))
        # 导入字体
        for one in fonts:
            QFontDatabase.addApplicationFont(one)

    def hideWidget(self):
        self.search.setVisible(False)

    def actions(self):
        self.pushButton.clicked.connect()
        input()

    def datainit(self):
        input()

    def ExpendAS(self):
        input()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MainApp()
    gui.show()
    sys.exit(app.exec_())