# 1.模拟搜索请求
- 创建http接口：
    - 初始化，传入config
    - 创建会话，随机User-Agent和Proxy
    - 接口analysis分析具体请求响应，截取请求数据
- 通过json配置搜索源,用json描述搜索源的请求方式与响应处理方式  
  例：
```json
{
  "name": "源名称",
  "authority": "源域名",
  "api": "源检索api",
  "method": "请求方式",
  "params": {
    "keyword": "检索关键字对应参数名",
    "title": "检索标题对应参数名",
    "author": "检索作者对应参数名",
    "dateFormat": "时间格式 yyyy-mm-dd,yyyy/mm/dd,yyyy,yy/mm等",
    "dateSt": "检索时间起始范围",
    "dateEnd": "检索时间结束范围",
    "dateRange": "检索时间范围"
  },
  "analysis": {
    "type": "响应类型 html 或 json",
    "html": [
      {
        "tag": "标签名",
        "attrs": {
          "辅助定位属性": "属性值"
        },
        "find": {
          "可以从该标签中找到的数据1": "该数据位置:text,href,src",
          "可以从该标签中找到的数据2": "该数据位置:text,href,src"
        }
      },
      {
        "tag" : "标签名",
        "attrs": {"辅助定位属性": "属性值"},
        "find": {
          "可以从该标签中找到的数据1": "该数据位置:text,href,src",
          "可以从该标签中找到的数据2": "该数据位置:text,href,src"
        }
      }
    ],
    "json": {
      "null": "数据空的判定索引键",
      "next_page": "下一页的索引键",
      "article_list": "数据列表的索引键",
      "title": "一条文献的标题的索引键",
      "author": "一条文献的作者的索引键",
      "date": "一条文献的发布日期的索引键",
      "type": "一条文献的类型的索引键",
      "dio": "一条文献的dio的索引键",
      "url": "一条文献的链接的索引键"
    }
  }
}
```

# 2.数据分析
- 基本数据格式
```json
{}
```
- 