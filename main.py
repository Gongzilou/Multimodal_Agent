"""  
主程序入口
"""

import uuid

from core.create_agent import Create_Agent
from utils.logger import log
from core.memory.connect_db import Postgres_DB
from langgraph.checkpoint.postgres import PostgresSaver
from core.memory.crud_chat_session import Crud_Chat_Session
from core.memory.get_short_memory import get_short_memory
import sys


# 开启新会话，自动生成thread_id
def loop_chat(
    crud: Crud_Chat_Session,
    agent: Create_Agent,
    user_id: str,
    # 只有旧会话需要checkpointer、thread_id
    checkpointer: PostgresSaver = None,
    thread_id: str = None
):

    # 继续上次会话，用旧的会话ID，映射表修改当前会话ID的活跃时间与过期时间
    if thread_id:
        my_thread_id = thread_id
        print(f"当前会话ID(旧):{my_thread_id}")
        # 修改活跃时间、过期时间
        crud.update_thread_id(thread_id=my_thread_id)
        # 展示之前的会话记录
        msg_list = get_short_memory(checkpointer=checkpointer,thread_id=thread_id)
        if msg_list:
            print("当前会话历史记录如下：")
            for msg in msg_list:
                print(msg)
        else:
            print("当前会话没有历史记录")
    
    # 开启新会话，用新的会话ID，映射表新增用户ID与会话ID的映射记录
    else:
        # 自动生成会话ID
        # 由uuid随机生成
        # python版本3.14及以上可以使用uuid7，
        # 优点：时间前缀 + 随机，有序，数据库索引性能好（uuid4无序，索引性能差）
        my_thread_id = str(uuid.uuid4())
        print(f"当前会话ID(新):{my_thread_id}")
        # 将用户ID与会话ID绑定存入映射表（每轮invoke结束后再将对话记录存入checkpointer相应的表里）
        crud.add_thread_id(thread_id=my_thread_id)


    
    # 开始循环对话
    
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
            thread_id=my_thread_id,
        )

        print(f"\nAI:\n{result}\n")
        count += 1


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
    # my_user_id = "Gongzilou"
    my_user_id = input("\n欢迎使用Agent,请输入您的用户名:\n").strip()
    log.info(f"当前用户ID:{my_user_id}")

    
    
    # 获取该用户的所有会话ID
    crud = Crud_Chat_Session(conn=db.conn,user_id=my_user_id)
    all_thread_id = crud.get_all_thread_id()
    print("\n" + "="*20 + "Agent对话开始(输入exit退出)" + "="*20 + "\n")
    # 已经有过会话记录的老用户
    if all_thread_id:
        print(f"用户{my_user_id}您好，检测到您是老用户，之前有以下会话记录:")
        # 存放会话ID和对应位置，后续根据用户输入的数字传入会话ID用于开启旧会话
        thread_dic = {}
        for i,thread_id in enumerate(all_thread_id,1):
            print(f"{i}: {thread_id}")
            # 用户输入的数字是字符串
            thread_dic[str(i)] = thread_id
        while True:
            user_input = input("\n请输入相应数字开启继续对话(输入0开启新对话,exit结束程序):\n").strip()
            if not user_input:
                print("不能为空，请输入内容")
                continue
            elif user_input.lower() == "exit":
                print("再见")
                sys.exit(0)
            elif user_input == "0":
                print("已为您开启新会话")
                loop_chat(crud=crud,agent=agent,user_id=my_user_id)
                break
            elif user_input in thread_dic:
                print("已为您继续上次会话")
                loop_chat(checkpointer=my_checkpointer,crud=crud,agent=agent,user_id=my_user_id,thread_id=thread_dic[user_input])
                break
            else:
                print("输入无效，请正确输入")
                continue
    
    # 还没有会话记录的新用户
    else:
        print(f"用户{my_user_id}您好，检测到您是新用户，目前还没有对话记录,已为您开启新会话")
        loop_chat(crud=crud,agent=agent,user_id=my_user_id)
        


    # 关闭数据库，释放连接
    db.close_db()





if __name__ == "__main__":
    main()