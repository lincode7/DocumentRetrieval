# 1.模拟搜索请求

- 创建http接口：
    - 初始化，传入config
    - 创建会话，随机User-Agent和Proxy
    - 接口analysis分析具体请求响应，截取请求数据
- 通过json配置搜索源,用json描述搜索源的请求方式与响应处理方式

```json
{
  "name": "源名称",
  "authority": "源域名 url",
  "api": "源检索api url",
  "method": "请求方式",
  "params_type": "参数类型，params，data等",
  "payload": {
    "datefmt": "yyyy-mm-dd,yyyy/mm/dd,yyyy/mm,yyyy等",
    "keyword": "key:@value  |   key:[key:@value]",
    "title": "key:@value    |   key:[key:@value]",
    "author": "key:@value   |   key:[key:@value]",
    "date": "key:@value     |   key:[key:@value]",
    "others": "key1:value1,key2:value2···"
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
          "可以从该标签中找到的数据1": "该数据位置:text,href等",
          "可以从该标签中找到的数据2": "该数据位置:text,href等"
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