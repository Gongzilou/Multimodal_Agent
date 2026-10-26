# 使用和风天气平台
```
和风天气平台使用两种凭据验证身份：JWT凭据 、 API KEY凭据
其中JWT凭据更为安全，它采用Ed25519算法进行签名，所以使用前需要先拥有Ed25519的密钥对
```

## 1、一次性生成密钥对(get_private_public_key.py)
```
使用 cryptography（密码学开源库）生成 ed25519 公私钥两份文档
妥善保存两份文档(private.key、public.key)
```

## 2、平台注册账号
```
平台注册账号，得到开发者ID、API Host；
创建项目，得到项目ID；
选择JWT凭据，然后将公钥复制给平台，得到凭据ID

API Host在发送请求时需要使用，
三个ID在生成动态JWT时需要使用
```

## 3、发送请求
```
每次发送请求前，使用 PyJWT（JWT开源库）+ 私钥 动态生成JWT（相当于API Key）(get_jwt.py)

平台根据公钥和生成的JWT进行验证，验证通过就返回响应

发送请求需要 API Host + JWT + 请求对应的其他参数（如查询天气需要经纬度等信息;查询城市需要城市名等信息）
```

# 环境配置 pip install ...
```
PyJWT==2.15.1
cryptography==50.0.2
```