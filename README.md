# Easy easy search
# 综合文献搜索工具
- 通过Requests向不同文献库网站构建session会话，搜索文献（关键字，作者，标题，时间范围，返回顺序）；
- 通过PySide2绘制ui界面；
- 本地存储文献过滤表，对搜索结果进行合并（同一文章合并url来源）、过滤，再进行显示；
- 不涉及服务器，所有网络请求都是程序模拟http请求向文献库进行搜索，本地只会产生添加到过滤表的历史记录。

---
* v1：2021-2月期间开发，能对nature进行查询并过滤本地论文标题列表，初步实现目的功能
![image](https://github.com/lincode7/search-for-essay-with-local-filter/blob/main/Filter/src/v1/v1.gif)

* v2：2021-2月到3月期间，开发库从pyqt5转pyside2，ui修改，增加其他搜索源（因QT部分代码冗余，中断多源结果的合并编写，转向v3开发）

* v3：2021-3月-4月期间，ui大改，代码优化，因课程项目暂停，预计7月重新进行
    - 8.12
        - 用bootstrap准备前端页面
    - 8.26
        - 代码模块化：
            - mian : 程序入口，初始化
            - UI : 主界面模块，UI刷新子线程模块
            - SEARCH : Http接口模块，Http会话子线程模块
            - DATA : 数据合并子线程
            - ERROR : 异常处理与日志模块
            - OTHERFUNCTION : 通用辅助函数模块
        - 

---