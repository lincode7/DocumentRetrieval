#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : main.py
# @Author: 胡煊林
# @Date  : 2021/8/26
# @Desc  : 程序入口，加载主界面

import sys
import time
import threading
import traceback

from v3.window import *
from v3.search import *
from v3.data import *
from v3.error import *


@coast_time
def appstart():
    App = MainApp()
    App.show()



if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        # App = MainApp()
        # App.show()
        appstart()
        sys.exit(app.exec_())
    except Exception as e:
        print(traceback.format_exc())
