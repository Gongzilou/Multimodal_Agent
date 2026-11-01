"""  
主程序入口

启动时会验证用户身份(Gongzilou)

游客：退出程序
用户：显示所有会话记录，开启新会话/继续某个会话/删除某个会话/删除所有会话/退出
"""
import sys
from core.memory.connect_db import Postgres_DB
from core.memory.crud_chat_session import Crud_Chat_Session
from core.create_agent import Create_Agent
import uuid
from core.memory.short_memory import Short_Memory
from langgraph.checkpoint.postgres import PostgresSaver




# 开始循环对话
def loop_chat(
    agent: Create_Agent,
    user_id: str,
    thread_id: str,
    crud: Crud_Chat_Session
): 
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
        
        # 用户按空格
        if not query:
            continue

        # 正式开始单论对话
        result = agent.ask(
            query=query,
            user_id=user_id,
            thread_id=thread_id,
        )

        print(f"\nAI:\n{result}\n")
        count += 1

        # 每一轮对话结束都需要对映射表中这个会话的活跃时间、过期时间进行更新
        crud.update_thread_id(thread_id=thread_id)





def main():
    print("="*30 + "页面1" + "="*30)
    print("="*30 + "页面1" + "="*30)
    print("="*30 + "页面1" + "="*30)
    print("\n" + "="*10 + "欢迎使用智能体Agent" + "="*10 + "\n")

    # 允许使用程序的用户，后续可以加入功能：注册用户，存入数据库
    alloud_user = ["Gongzilou",]

    # 验证身份
    user_id = input("\n请输入身份ID:\n").strip()
    # 验证未通过
    print("="*30 + "页面2" + "="*30)
    print("="*30 + "页面2" + "="*30)
    print("="*30 + "页面2" + "="*30)
    if user_id not in alloud_user:
        print("\n很抱歉，您暂时没有使用权限\n")
        sys.exit(0)

    # 验证通过
    print("="*30 + "页面2" + "="*30)
    print("="*30 + "页面2" + "="*30)
    print("="*30 + "页面2" + "="*30)
    print(f"\n您好，{user_id}\n")
    # 创建数据库连接
    my_db = Postgres_DB() # 初始化数据库
    my_db.open_db() # 开启数据库连接
    my_conn = my_db.conn # 获取连接
    # 创建检查点checkpointer
    my_checkpointer = PostgresSaver(my_conn)
    # 自动建表（四张存储checkpointer元数据、对话记录的表）
    my_checkpointer.setup()  
    # 初始化agent，同时赋予短期记忆能力
    my_agent = Create_Agent(checkpointer=my_checkpointer)
    
    
    # 用户选择界面
    while True: 

        # 展示所有会话记录（目前是会话ID，后续可以改成摘要）
        crud = Crud_Chat_Session(conn=my_conn,user_id=user_id) # 初始化
        thread_id_list = crud.get_all_thread_id() # 查询该用户的所有会话ID
        thread_ids_dic = {} # 存放会话ID与对应数字，后续根据用户选择的数字，继续相应的旧会话
        print("以下是您所有会话记录:")
        for i,thread_id in enumerate(thread_id_list,1):
            thread_ids_dic[str(i)] = thread_id
            print(f"  {i}、{thread_id}")

        print("\n1: 新建会话 | 2: 删除单个会话 | 3: 删除全部会话 | 4: 继续旧会话 | 0: 退出程序\n")
        user_choice = input("请输入您的选择:\n").strip()
        print("="*30 + "页面3" + "="*30)
        print("="*30 + "页面3" + "="*30)
        print("="*30 + "页面3" + "="*30)
        if user_choice not in ["0","1","2","3","4"]:
            print("请输入正确内容！")
            continue
        if user_choice == "0":
            print("再见")
            break
        if user_choice == "1":
            # 生成新的会话ID
            new_thread_id = str(uuid.uuid4())
            # 将用户ID与会话ID存入映射表
            crud.add_thread_id(thread_id=new_thread_id)
            # 开始循环对话
            print(f"\n当前会话ID(新): {new_thread_id}\n")
            loop_chat(agent=my_agent,user_id=user_id,thread_id=new_thread_id,crud=crud)
            continue
        if user_choice == "2":
            #这里只能输入会话ID对应的序号
            user_input_index = input("\n请选择要删除的会话(只能输入会话ID对应的序号):\n").strip()
            need_delete_thread_id = thread_ids_dic[user_input_index]
            
            # 先删除checkpointer相关表的内容
            short_memory = Short_Memory(checkpointer=my_checkpointer,thread_id=need_delete_thread_id)
            is_true = short_memory.delete_messages()
            if is_true:
                # 后删除映射表内容
                crud.delete_thread_id(need_delete_thread_id)
            continue
        if user_choice == "3":
            
            # 先删除checkpointer相关表的内容
            for row in thread_ids_dic.values():
                short_memory = Short_Memory(checkpointer=my_checkpointer,thread_id=row)
                is_true = short_memory.delete_messages()
                if is_true:
                    # 后删除映射表内容
                    crud.delete_thread_id(row)
            # # 后删除映射表内容
            # crud.delete_user_id()
            continue
        if user_choice == "4":
            #这里只能输入会话ID对应的序号
            thread_index = input("\n请选择要继续的会话(只能输入会话ID对应的序号):\n").strip()
            # 沿用旧的会话ID
            old_thread_id = thread_ids_dic[thread_index]
            # 展示对话历史
            short_memory = Short_Memory(checkpointer=my_checkpointer,thread_id=old_thread_id)
            msg_list = short_memory.get_messages()
            print("\n对话历史如下:\n")
            for msg in msg_list:
                print(msg)
            print("\n开始新一轮对话:\n")
            # 开始循环对话 
            print(f"\n当前会话ID(旧): {old_thread_id}\n")  
            loop_chat(agent=my_agent,user_id=user_id,thread_id=old_thread_id,crud=crud)
            continue



    my_db.close_db() # 断开数据库连接
   




if __name__ == "__main__":
    # import logging
    # from utils.logger import log
    # for h in log.handlers[:]:
    #     if isinstance(h,logging.StreamHandler):
    #         log.removeHandler(h)



    main()



