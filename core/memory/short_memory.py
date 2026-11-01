"""  
查询或删除当前会话ID下的历史对话记录

相关表格：
1、checkpoints: 会话快照主表（每一轮状态快照）
2、checkpoint_blobs: 二进制 blob 表，用户的 messages 消息主体存在这里
3、checkpoint_writes: 节点中间写入、断点续跑的临时数据

checkpoint_migrations: 框架迁移版本表，不会被改动
"""
import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).parent.parent.parent
    )
)





from langgraph.checkpoint.postgres import PostgresSaver

from utils.logger import log

class Short_Memory:
    # 初始化，获取checkpointer、thread_id
    def __init__(self,checkpointer: PostgresSaver,thread_id: str):
        self.checkpointer = checkpointer
        self.thread_id = thread_id
        self.config = {
            "configurable":{
                "thread_id":thread_id
            }
        }

    # 查询该thread_id下的历史消息
    def get_messages(self):
        state = self.checkpointer.get(self.config)
        # 没有对话记录
        if not state:
            log.warning(f"当前会话没有对话记录,thread_id={self.thread_id}")
            return []
        # 提取对话记录进行存储并一次性返回
        msg_list = []
        messages = state["channel_values"]["messages"]
        for msg in messages:
            # 目前只有纯字符串
            # 后续新增多模态再对content内容进行判断
            msg_list.append(f"【{msg.type}】\n  {msg.content}")
        return msg_list

    # 删除该thread_id下的历史消息(映射表记录也要相应删除)
    def delete_messages(self):
        try:
            self.checkpointer.delete_thread(self.thread_id)
            log.info(f"已删除该会话的真实历史记录,thread_id={self.thread_id}")


            
            # 删除后立刻自查，用同一个连接重新get
            state = self.checkpointer.get(self.config)
            if state:
                log.warning(f"⚠️ delete_thread执行完毕，但仍然查到state! thread_id={repr(self.thread_id)}")
            else:
                log.info(f"✅ 删除后本连接查询无状态，thread_id={repr(self.thread_id)}")

            
            
            return True
        except Exception as e:
            error_msg = f"删除会话记录失败:\n{str(e)}"
            log.exception(error_msg)
            return False





if __name__ == "__main__":
    from core.memory.connect_db import Postgres_DB
    db = Postgres_DB()
    db.open_db()

    conn = db.conn
    checkpointer = PostgresSaver(conn)
    thread_id = "test"
    short_memory = Short_Memory(checkpointer=checkpointer,thread_id=thread_id)
    msg_list = short_memory.get_messages()
    print(msg_list)

    db.close_db()




