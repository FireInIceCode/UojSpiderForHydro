# UOJ->Hydro转换器

## 简介

可以爬取题面和数据,传统题可以自动根据problemconf配置生成config.yaml.并转化成Hydro格式,可以直接压缩导入.

需要管理员权限账户.

## 使用

新建配置文件xx.py,写入信息
```python
basepath='./problem/' # path to save problems
skip = True # Skip problem which has downloaded(exists folder)
only_public = True # Only download the public problem(not hidden)
url = 'http://uoj.ac' # Site's url
pre = 'U' # Id prefix
extags=['uoj'] # Tags to add
defaulttags=['待标记'] # Default tags for problems has no tags
# template for problem.yaml
templ =\
    '''
pid: {pid}
owner: 1
title: "{title}"
tag:
{tags}
nSubmit: 0
nAccept: 0
'''
retry_cnt = 3 # retry times when failed
```

然后运行spider.py,输入cookie和上面配置文件模块路径(python模块导入路径方式).支持命令
- all 下载所有题
- ps [pids] 下载指定题号,多个题目id用空格分隔
- cookie [newcookie] 重设cookie
- quit 退出