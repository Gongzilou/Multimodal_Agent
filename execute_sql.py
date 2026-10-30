"""  
查看数据库中每个会话ID下的对话记录
"""

import psycopg
from langgraph.checkpoint.postgres import PostgresSaver

postgres_url = "postgresql://postgres:12345@localhost:5432/Multimodal_Agent_Memory?sslmode=disable"

def list_all_threads(conn):
    # 直接SQL拿全部thread_id
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT thread_id FROM checkpoints ORDER BY thread_id;")
        rows = cur.fetchall()
        return [r[0] for r in rows]

def print_one_thread(checkpointer, thread_id):
    config = {"configurable": {"thread_id": thread_id}}
    state = checkpointer.get(config)
    if not state:
        print(f"\n===== thread:{thread_id} 无状态 =====\n")
        return
    messages = state["channel_values"]["messages"]
    print(f"\n==================== Thread: {thread_id} ====================")
    for msg in messages:
        print(f"【{msg.type}】")
        if isinstance(msg.content, list):
            for item in msg.content:
                if item["type"] == "text":
                    print("  text:", item["text"])
                elif item["type"] == "image_url":
                    print("  [图片]")
        else:
            print("  ", msg.content)

def delete_all(conn):
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE checkpoints, checkpoint_blobs, checkpoint_writes;")
    conn.commit()
    print("已清空所有checkpoint会话数据，表结构保留")

if __name__ == "__main__":
    with psycopg.connect(postgres_url) as conn:

        # # 删除所有会话记录
        # delete_all(conn)
        
        # 获取所有会话ID
        thread_list = list_all_threads(conn)
        print(f"一共找到 {len(thread_list)} 个会话：")
        checkpointer = PostgresSaver(conn)
        # 查询每个会话ID下的对话记录
        for tid in thread_list:
            print_one_thread(checkpointer, tid)

        


























""" 



# 建表

CREATE TABLE chat_session (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    thread_id TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_active_at TIMESTAMPTZ DEFAULT NOW(),
    expire_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '30 days'
);

-- 索引
CREATE INDEX idx_chat_session_user_id ON chat_session(user_id);
CREATE INDEX idx_chat_session_thread_id ON chat_session(thread_id);
CREATE INDEX idx_chat_session_last_active ON chat_session(last_active_at);
CREATE INDEX idx_chat_session_expire_at ON chat_session(expire_at); 





追加字段

ALTER TABLE chat_session ADD COLUMN expire_at TIMESTAMPTZ;
-- 给已有存量数据初始化expire_at
UPDATE chat_session SET expire_at = last_active_at + INTERVAL '30 days';
-- 新增索引
CREATE INDEX idx_chat_session_expire_at ON chat_session(expire_at);






每次invoke之后更新字段

UPDATE chat_session
SET last_active_at = NOW(),
    expire_at = NOW() + INTERVAL '30 days'
WHERE thread_id = %s AND user_id = %s;

"""
