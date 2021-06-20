# 检 索 论 文 数 据 库

## 程序逻辑
1. 数据处理
- 一条基本数据：
> one = {'title': , 'author': , 'date': , 'url': }
- 一个网站的返回数据：
> data = [one, two, ···]
- 最终数据：
> data = [one, two, ···] (去重与整合url)
2. ui传参
- 一条请求体：
>   
    {
        'first': {'keyword':'', 'author':'', 'title':''}, 
        'others': [
            {
                'logic':and\or\not, 
                'key_1':value_1
            },
            ...,
            {
                 'logic':and\or\not, 
                 'key_9':value_9
            },
        ],
        'page' : 1,
        'psize' : 200,
        'date' : [st, end],
        'order' : 'relevance'
    } 
---

## https://www.nature.com/ ##
+ 不支持and or not
+ 方法：GET
+ 请求url: https://www.nature.com/search 或 https://www.nature.com/search/ajax
+ 数据体作为param传入：
```
    'q' : str,    关键词
    'author' : str    作者
    'title' : str     标题
    'date_range': 'y-y',   时间/null
    'order' : 'relevance', /date_desc /date_asc 返回数据顺序，相关性和最新和最老，默认relevant
    'page' : 1,
```
+ 返回HTML
+ test:`https://www.nature.com/search/ajax?q=Protein&order=relevance&date_range=2015-2021&page=1`
---

## https://www.sciencemag.org/ ##
+ 不支持and or not
+ 方法：POST
+ 请求url: https://w35slb9cf3.execute-api.us-west-1.amazonaws.com/prod/search
+ 数据体作为json传入：
```
{
    'page':1,
    'pagesize':50,
    'orderby':'tfidf',   /oldest /newest  返回数据顺序，相关性和最新和最老，默认tfidf
    'rules':[
        {'field':'q','value':'123'},
        {"field":"author_surnames","value":"a"},
        {'field':'title','value':'123'},
        {'field':'pubdate','value':[y-m-d,y-m-d]},  /null
        {'field':'source','value':'\'sciencemag\' \'Science\' \'Science Advances\' \'Science Signaling\' \'Science Translational Medicine\' \'Science Immunology\' \'Science Robotics\' \'In the Pipeline\' \'Sciencehound\' \'Science Careers Blog\' \'Books, Et Al.\''}
    ]
}
```
+ 返回json数据
+ test:`{"page":1,"pagesize":10,"orderby":"tfidf","rules":[{"field":"q","value":"protein"}]}`
---

## http://apps.webofknowledge.com/WOS_GeneralSearch_input.do?product=WOS&SID=8E7fLauu3lh5htIOpoR&search_mode=GeneralSearch ##

---

## https://www.sciencedirect.com/ ##
+ 方法：GET
+ 请求url: https://www.sciencedirect.com/search/api
+ 数据体作为param传入：
    ```
  {
        'qs': '1'
        'authors': '2'
        'affiliations': '2001-2015'
        'title': '3'
        'sortBy':'relevance' /date 相关性和最新，没有最旧
    }
  ```
+ 返回json
+ test: ``
---

## https://pubs.acs.org/ ##
+ 方法：GET
+ 请求url: https://search.acs.org/content/search/acs/en/search.advanced.html
+ 传入方式：
```buildoutcfg

```
+ test: `https://search.acs.org/content/search/acs/en/search.html?q=1&allTerms=2&exactPhrase=3&withoutTerms=4&filter_type_include=true&filter_type_value=&afterDate=2020-11-01&beforeDate=2021-02-28&containsWordsInTitle=5`

---

## https://link.springer.com/ ##
    # 方法：GET
    # 请求url: https://link.springer.com/search

    https://link.springer.com/search?date-facet-mode=between&facet-start-year=2020&showAll=true&facet-end-year=2021&dc.title=5&query=1+AND+%222%22+AND+%283%29+AND+NOT+%284%29&dc.creator=6
    test: 
---

## https://www.tandfonline.com/ ##
    # 方法：GET
    # 请求url: https://www.tandfonline.com/action/doSearch

    https://www.tandfonline.com/action/doSearch?field1=Keyword&text1=1&field2=Title&text2=2&field3=Contrib&text3=3&field4=Title&text4=4&field5=Contrib&text5=5&Ppub=&AfterYear=2008&BeforeYear=2018
    test: 
---

## https://pubs.rsc.org/ ##
    # 方法：GET
    # 请求url: https://pubs.rsc.org/en/results/all

    https://pubs.rsc.org/en/results/all?Category=All&AllText=1&ExactText=3&AtleastText=2&WithoutText=4&IncludeReference=false&SelectJournal=false&DateRange=true&Title=9&AuthorGivenName0=6&AuthorFamilyName0=5&AuthorGivenName1=8&AuthorFamilyName1=7&SelectDate=true&DateToYear=2018&DateFromYear=2008&DateFromMonth=01&DateToMonth=09&PriceCode=False&OpenAccess=false
    test: 
---

## https://onlinelibrary.wiley.com/##
    # 方法：GET
    # 请求url: 
---

数据存储需求
爬取数据表,dict，包括标题，作者，出版时间，url，每个元素都是list
filter_data = { 'info':[{同filter_data},{同filter_data},{同filter_data},````], 'url':[[1,2,3,4,5],[1,2,3,4,5],[1,2,3,4,5],````],}
本地过滤表,dict，包括标题
filter_data = ['title1','title2','title3',````]
后者无需本地存储，每次访问变化
逻辑如下
查询并通过table3进行过滤产生table1,2


---

# 设置：
1. 网络设置：
    (1) 请求头
    (2) 代理地址
2. ui设置：
    








