# 版本1
- 实现了nature的网页搜索接口  
利用request实现基础访问;  
利用bs4实现数据截取;
- 实现了基础的过滤表  
本地文件以json格式保存;  
- 实现多线程界面流畅性初步优化  
搜索子线程：按需请求，通过qt的signal传出结果;  
界面数据刷新子线程：通过子线程添加数据展示的控件，避免页面卡顿;