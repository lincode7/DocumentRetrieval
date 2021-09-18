#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : main.py
# @Author: 胡煊林
# @Date  : 2021/8/26
# @Desc  :

import sys
import time
import threading
import traceback

# 导入界面模块
# 导入界面刷新子线程模块

# 导入搜索子线程模块



if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        App = MainApp()
        print('窗口初始化耗时：', time.time() - st)
        App.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(traceback.format_exc())
