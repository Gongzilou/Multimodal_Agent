"""  
对用户的会话记录进行增删改查——只针对chat_session映射表
"""
import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).parent.parent.parent
    )
)





from psycopg import Connection

from utils.logger import log


# 查：获取该用户的所有会话ID
# 可以用来进行会话的权限验证等
def get_all_thread_id(conn: Connection,user_id: str):
    sql = """  
    select thread_id 
    from chat_session 
    where user_id = %s 
    order by last_active_time desc;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql,(user_id,))
            list_thread_id = [data[0] for data in cur.fetchall()]
        if not list_thread_id:
            log.warning(f"用户{user_id}还没有会话记录")
        else:
            log.info(f"已获取用户{user_id}所有会话ID:\n{list_thread_id}")
        return list_thread_id
    except Exception as e:
        error_msg = f"执行SQL获取会话ID出错:\n{str(e)}"
        log.exception(error_msg)
        raise



# 增：为该用户新增会话记录
# 每次invoke结束进行新增
# 真正对话记录存在checkpoint_blobs表中
def add_thread_id(conn: Connection, user_id: str, thread_id: str):
    sql="""  
    insert into 
    chat_session(user_id,thread_id)
    values(%s,%s)
    returning id;
    """  
    try:
        with conn.cursor() as cur:
            cur.execute(sql,(user_id,thread_id,))
            new_id = cur.fetchone()[0]
        log.info(f"已为用户存储新的会话,id={new_id},thread_id={thread_id}")
    except Exception as e:
        error_msg = f"执行SQL新增会话ID出错:\n{str(e)}"
        log.exception(error_msg)
        raise



# 删：删除该用户指定的某几条会话记录
# 对于checkpoint_blobs表中的真正记录也要删除
def delete_thread_id(conn: Connection, user_id: str, thread_id_list: list[str]):
    sql="""  
    delete
    from chat_session
    where
    user_id = %s
    and
    thread_id = any(%s);
    """
    if not thread_id_list: # 防止空列表，不属于None
        log.warning("暂时没有会话记录需要删除")
        return
    try:
        with conn.cursor() as cur:
            cur.execute(sql,(user_id,thread_id_list,))
            # 获取本次实际删除的行数（判断是否对不存在的内容进行删除）
            really_delete_count = cur.rowcount
        log.info(f"已删除指定会话记录:\nuser_id={user_id}\nthread_id={thread_id_list}\n实际删除行数:{really_delete_count}")
        if really_delete_count != len(thread_id_list):
            log.warning("实际删除行数与要删除的数量不匹配")
        return
    except Exception as e:
        error_msg = f"执行SQL删除会话ID出错:\n{str(e)}"
        log.exception(error_msg)
        raise



# 删：删除该用户所有会话记录
# 对于checkpoint_blobs表中的真正记录也要删除
# checkpointer.delete是根据thread_id删除的，所以这里需要先查询返回要删除的所有thread_id，然后再删除
def delete_user_id(conn: Connection, user_id: str):
    sql_get="""  
    select thread_id
    from chat_session
    where
    user_id = %s;
    """
    
    sql_delete="""  
    delete
    from chat_session
    where
    user_id = %s;
    """
    try:
        with conn.cursor() as cur:
            # 先获取所有要删除的thread_id，给外层checkpointer.delete
            cur.execute(sql_get,(user_id,))
            need_delete_thread_id = [data[0] for data in cur.fetchall()]
            # 再删除映射表的相应部分
            cur.execute(sql_delete,(user_id,))
            really_delete_count = cur.rowcount
        if really_delete_count == 0:
            log.warning(f"用户{user_id}还没有会话记录")
        else:
            log.info(f"已删除用户{user_id}的所有会话记录，实际删除行数:{really_delete_count}")

        return need_delete_thread_id
    except Exception as e:
        error_msg = f"执行SQL删除用户ID出错:\n{str(e)}"
        log.exception(error_msg)
        raise



# 改：修改某条会话记录的最后活跃时间、过期时间
# 用户开启旧会话后，每次invoke结束进行修改，只是单纯查看对话记录就不用修改
# checkpoint_blobs表中的真正对话记录存也要进行更新增加
def update_thread_id(conn: Connection, user_id: str, thread_id: str):
    sql="""  
    update chat_session
    set
    last_active_time = now(),
    expire_time = now() + interval '30 days'
    where
    user_id = %s
    and
    thread_id = %s;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql,(user_id,thread_id,))
            really_update_count = cur.rowcount
        if really_update_count == 0:
            log.warning(f"用户{user_id}没有这个会话,thread_id={thread_id}")
        else:
            log.info(f"已更新会话的活跃时间和过期时间,thread_id={thread_id}")
    except Exception as e:
        error_msg = f"执行SQL修改会话ID出错:\n{str(e)}"
        log.exception(error_msg)
        raise










if __name__ == "__main__":
    from core.memory.connect_db import Postgres_DB
    db = Postgres_DB()
    db.open_db()
    my_user_id = "test_user"



    # # 增
    # import uuid
    # my_thread_id = str(uuid.uuid4())
    # add_thread_id(conn=db.conn,user_id=my_user_id,thread_id=my_thread_id)



    # # 删——thread_id
    # my_thread_id_list = [
    #     "7bb8aa70-352f-4e49-b79a-b4eeb34e3cb8",
    #     "d8d08ce9-babc-437e-a397-eae48709e754"
    # ]
    # delete_thread_id(conn=db.conn,user_id=my_user_id,thread_id_list=my_thread_id_list)



    # # 删——user_id
    # need_delete_thread_id_list = delete_user_id(conn=db.conn,user_id=my_user_id)
    # print(f"已删除{len(need_delete_thread_id_list)}条会话记录:\n{need_delete_thread_id_list}")



    # # 改
    # update_thread_id(conn=db.conn,user_id=my_user_id,thread_id="b00b0423-30c4-4408-8c0f-db8cec0d03b1")
    
    

    # 查
    result = get_all_thread_id(conn=db.conn,user_id=my_user_id)
    print(f"用户{my_user_id}的会话记录数量:{len(result)}")

    
    
    db.close_db()

