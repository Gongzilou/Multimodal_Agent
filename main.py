"""  
主程序入口
"""

import uuid

from core.create_agent import Create_Agent
from utils.logger import log
from core.memory.connect_db import Postgres_DB
from langgraph.checkpoint.postgres import PostgresSaver
from core.memory.crud_chat_session import get_all_thread_id


def main():

    # 初始化数据库
    db = Postgres_DB()
    # 连接数据库
    db.open_db()
    # 创建短期记忆持久化存储机制checkpointer
    my_checkpointer = PostgresSaver(db.conn)
    # 自动建表（四张存储checkpointer元数据、对话记录的表）
    my_checkpointer.setup()
    
    # 初始化agent，同时赋予短期记忆能力
    agent = Create_Agent(checkpointer=my_checkpointer)

    # 接收长期记忆标志：user_id
    # 暂时随便写一个（后续将改为用户登入ID）
    user_id = "Gongzilou"
    log.info(f"当前用户ID:{user_id}")

    
    
    # 获取该用户的所有会话ID
    all_thread_id = get_all_thread_id()
    if all_thread_id:
        print("开发中...")
    else:
        print("您目前还没有对话记录,已为您开启新会话")
        # 自动生成会话ID
        # 由uuid随机生成
        # python版本3.14及以上可以使用uuid7，
        # 优点：时间前缀 + 随机，有序，数据库索引性能好（uuid4无序，索引性能差）
        thread_id = str(uuid.uuid4())
        log.info(f"当前会话ID:{thread_id}")

    
    
    
    
    
    
    
    
    
    # 接收短期记忆标志：thread_id
    # 由uuid随机生成
    # python版本3.14及以上可以使用uuid7，
    # 优点：时间前缀 + 随机，有序，数据库索引性能好（uuid4无序，索引性能差）
    thread_id = str(uuid.uuid4())
    log.info(f"当前会话ID:{thread_id}")

    # 开始循环对话
    print("\n" + "="*20 + "Agent对话开始(输入exit退出)" + "="*20 + "\n")
    # 对话轮次
    count = 1
    while True:
        print("="*10 + f"第{count}轮对话" + "="*10)
        # 用户输入的问题
        query = input("\n用户:\n").strip()

        # 退出程序
        if query.lower() == "exit":
            print("\nAI:\n再见\n")
            break
        
        # 用户按错成换行
        if not query:
            continue

        # 正式开始单论对话
        # 后续要对user_id和thread_id做匹配验证
        result = agent.ask(
            query=query,
            user_id=user_id,
            thread_id=thread_id,
        )

        print(f"\nAI:\n{result}\n")
        count += 1

    # 关闭数据库，释放连接
    db.close_db()





if __name__ == "__main__":
    main()