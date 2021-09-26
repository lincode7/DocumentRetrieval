
# 综合文献搜索工具
- 通过Requests向不同文献库网站构建session会话，搜索文献（关键字，作者，标题，时间范围，返回顺序）；
- 通过PySide2绘制ui界面；
- 本地存储文献过滤表，对搜索结果进行合并（同一文章合并url来源）、过滤，再进行显示；
- 不涉及服务器，所有网络请求都是程序模拟http请求向文献库进行搜索，本地只会产生添加到过滤表的历史记录。

## 开发环境
- Windows 10 1909
- PyCharm 2021.2.2 （Community Edition）
- Python 3.7
- 第三方库：
    1. requests：HTTP库，用于本地并发http请求；
    2. beautifulsoup：网页解释库，提供lxml的支持；
    3. PyQt5：Python下的Qt库
    4. designer：绘制ui界面，利用qss美化

---
* v1：2021-2月期间开发，能对nature进行查询并过滤本地论文标题列表，初步实现目的功能
![image](https://github.com/lincode7/search-for-essay-with-local-filter/blob/main/Filter/src/v1/v1.gif)

* v2：2021-2月到3月期间，开发库从pyqt5转pyside2，ui修改，增加其他搜索源，合并数据去重效果不理想

* v3：2021-7月-，ui大改，代码优化
    - 8.26
      - 模式优化
        - 动态添加搜索源，通过填写表格，生成http响应分析逻辑，获取搜索结果并加入结果列表
        - 记录异常日志（时间，异常位置，异常信息）
        - 搜索结果时间排序
        - 
      - 代码模块化：
        - mian : 程序入口，初始化
        - window : 主界面模块，UI刷新子线程模块
        - search : Http接口模块，Http会话子线程模块
        - data : 数据合并子线程
        - error : 异常处理与日志模块
        - helpfunc : 通用辅助函数模块

---
