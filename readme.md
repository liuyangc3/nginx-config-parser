# 介绍 
通过 HTTP接口用来 查看/添加/删除 Nginx 反向代理的节点


# 原理
通过类似于 lex/yacc 的词法和语法分析，解析nginx upstream文本配置，并生成对象

通过接口操作对象内的数据，并生成新的upstream文本配置。

在config.py中指定Nginx Home和upstream配置文件的位置


lua 分支使用lpeg 实现

# 依赖
```
pip install tornado simplejson ply
```
# Nginx config
```
http {
    ...
    # upstream config must in a file
    # include this file here and set it's path in config.py too.
    include upstream.conf;
    ...
    }
```

run tornado on same host which Nginx runs too  

# web api
upsteam config in Nginx
```
upsteam test1 {
    ip_hash,
    server 192.168.0.1:80  max_fails=1 fail_timeout=10s;
}

upsteam test2 {
    server 192.168.0.2:81  max_fails=1 fail_timeout=10s;
    server 192.168.0.2:82  max_fails=1 fail_timeout=10s;
}
```

upsteam config json format mapping
```
{
    "test1" : [
        "ip_hash",
        ["192.168.0.1:80", "1", "10s"],
    ],
    
    "test2": [
        ["192.168.0.2:81", "1", "10s"],
        ["192.168.0.2:82", "1", "10s"]
    ]
}
```


## 获取upsteam配置
curl 127.0.0.1:8000/
```
{"ggpt": ["ip_hash", ["10.201.10.124:8080", "1", "10s"], ["10.201.10.224:8080", "1", "10s"]], 
"passport": ["ip_hash", ["10.201.10.126:8080", "1", "10s"], ["10.201.10.226:8080", "1", "10s"]]}
```
参数pretty可以生成可阅读格式

curl 127.0.0.1:8000/?pretty
```
{
    "ggpt": [
        "ip_hash",
        [
            "10.201.10.124:8080",
            "1",
            "10s"
        ],
        [
            "10.201.10.224:8080",
            "1",
            "10s"
        ]
    ],
    "passport": [
        "ip_hash",
        [
            "10.201.10.126:8080",
            "1",
            "10s"
        ],
        [
            "10.201.10.226:8080",
            "1",
            "10s"
        ]
    ],
}
```

## 列出所有的 upstream name 以及 server的数量
curl 127.0.0.1:8000/list
```
Name:                         Servers:
ggpt                          2
passport                      2
imapi                         2
cas                           2
sh                            2
```

## 查询指定 upstream 
curl 127.0.0.1:8000/pm?pretty
```
[
    [
        "10.201.10.125:8080",
        "1",
        "10s"
    ],
    [
        "10.201.10.225:8080",
        "1",
        "10s"
    ]
]

```
## 给指定 upstream 添加 server
curl -XPOST 127.0.0.1:8000/pm?pretty -d '["10.201.10.233:3333", "111", "10s"]'
```
[
    [
        "10.201.10.125:8080",
        "1",
        "10s"
    ],
    [
        "10.201.10.225:8080",
        "1",
        "10s"
    ],
        [
        "10.201.10.233:3333",
        "111",
        "10s"
    ]
]
```


## 删除server
curl -XDELETE 127.0.0.1:8000/pm?pretty -d '10.201.10.233'
```
[
    [
        "10.201.10.125:8080",
        "1",
        "10s"
    ],
    [
        "10.201.10.225:8080",
        "1",
        "10s"
    ]
]
```
