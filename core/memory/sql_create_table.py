"""  
创建数据库表chat_session

映射user_id与thread_id

只执行一次



# 建表SQL

CREATE TABLE chat_session (
    id BIGSERIAL PRIMARY KEY, # 自增主键,BIGSERIAL比int范围更大,不容易溢出
    user_id TEXT NOT NULL, # 一个user_id映射多个thread_id
    thread_id TEXT NOT NULL UNIQUE, # 每个会话一个id,UNIQUE表示整张表的thread_id不能重复
    created_time TIMESTAMPTZ DEFAULT NOW(), # 会话创建时间
    last_active_time TIMESTAMPTZ DEFAULT NOW(), # 会话最后活跃时间
    expire_time TIMESTAMPTZ DEFAULT NOW() + INTERVAL '30 days' # 会话到期时间：最后活跃时间 + 30天
);

-- 索引
CREATE INDEX idx_user_id ON chat_session(user_id);
CREATE INDEX idx_thread_id ON chat_session(thread_id);
CREATE INDEX idx_last_active_time ON chat_session(last_active_time);
CREATE INDEX idx_expire_time ON chat_session(expire_time); 

"""
import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).parent.parent.parent
    )
)





from core.memory.connect_db import Postgres_DB
from utils.logger import log

# 初始化数据库
db = Postgres_DB()

# 创建数据库连接
db.open_db()

# 建表与建索引的SQL
sql_create_table = """ 
create table chat_session(
    id bigserial primary key,
    user_id text not null,
    thread_id text not null unique,
    created_time timestamptz default now(),
    last_active_time timestamptz default now(),
    expire_time timestamptz default now() + interval '30 days'
);
"""
# 分开执行，防止其中某个出错
sql_create_index = [
    "create index idx_user_id on chat_session(user_id);",
    "create index idx_thread_id on chat_session(thread_id);",
    "create index idx_last_active_time on chat_session(last_active_time);",
    "create index idx_expire_time on chat_session(expire_time);"
]

# 创建游标，执行sql
try:
    with db.conn.cursor() as cur:
        # 建表
        cur.execute(sql_create_table)
        # 建索引
        for sql in sql_create_index:
            cur.execute(sql)
    log.info("映射表与索引创建完成")
except Exception as e:
    error_msg = f"执行SQL失败:\n{str(e)}"
    log.exception(error_msg)
    raise
finally:
    # 关闭数据库连接
    db.close_db()





