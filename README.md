# Flask-Blog
#### 模板数据传递结构

```
pages 导航栏
[
    {
        'name':'xxx',
        'href':'aaa'
    },
]
```

```
posts 文章缩略
[
    {
        'title':'xxx',
        'href':'xxx',
        'ad':'xxx',
        'more':'xxx'
    },
]
```

```
mp 文章目录
[
    {
        'time':'xxx',
        'articles': [
            {
                'title':'xxx',
                'href':'xxx',
                'date':'xxx'
            },
        ]
    },
]
```