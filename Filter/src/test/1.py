# -*- coding: utf-8 -*-
import sys, time
from PySide2.QtCore import QFile, QIODevice, Slot
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QApplication, QMessageBox


class MainApp(QMainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        self.importResource()
        self.hideWidget()
        self.actions()
        self.datainit()

    # 动态加载ui
    def importResource(self):
        st = time.time()
        # 导入ui
        ui_path = r'widget.ui'
        ui_file = QFile(ui_path)
        if not ui_file.open(QIODevice.ReadOnly):
            print("Cannot open {}: {}".format(ui_path, ui_file.errorString()))
            sys.exit(-1)
        self.ui = QUiLoader().load(ui_file, None)
        ui_file.close()
        end = time.time()
        print("spend:", end - st)

    def hideWidget(self):
        self.ui.labeltest.setVisible(False)
        print('h')

    def actions(self):
        self.ui.pushButtontest.clicked.connect(self.press)
        print('a')

    def datainit(self):
        print('d')

    @Slot()
    def press(self):
        QMessageBox.warning(self, "warning", "button is pressed")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MainApp()
    gui.ui.show()
    sys.exit(app.exec_())