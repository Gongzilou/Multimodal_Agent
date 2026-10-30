# 短期记忆
```
用户的短期记忆存储在postgressql数据库。
每次invoke调用该thread_id下的对话记录时，
如果超过上下文窗口大小（本主控模型适配50轮），
就保留最近25轮对话，之前的做摘要放在最前面
```

## 先在数据库创建一张user_id与thread_id的映射表chat_session（sql_create_table.py）
```
字段：
id：自增主键，BIGSERIAL类型（比int类型范围更广，防止溢出）
user_id：用户ID，text类型（varchar有长度限制）
thread_id：会话ID，text类型，设置为UNIQUE（整张表的thread_id不能重复）
created_time：创建时间，TIMESTAMPTZ类型，默认值now()
last_active_time：上次活跃时间，TIMESTAMPTZ类型，默认值now()
expire_time：过期时间，活跃时间+自定义天数（默认30天），TIMESTAMPTZ类型，默认值now()+INTERVAL '30 days'
```

## 存储时机
```
每次invoke结束进行会话存储：
对话记录存在checkpoint_blobs表中；
新会话就对chat_session进行新增（user_id，thread_id）；
旧会话就对chat_session进行更新（该thread_id下的last_active_time、expire_time）
```

## 删除时机
```
1、用户主动删除某个thread_id
2、过期时间前3天进行提醒展示，到过期时间进行删除
```

