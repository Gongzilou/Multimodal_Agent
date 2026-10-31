"""  
获取当前会话ID下的历史对话记录
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


# 根据thread_id获取历史对话记录
def get_short_memory(checkpointer: PostgresSaver,thread_id: str):
    config = {
        "configurable":{
            "thread_id":thread_id
        }
    }
    state = checkpointer.get(config=config)
    # 没有对话记录
    if not state:
        log.warning(f"当前会话没有对话记录,thread_id={thread_id}")
        return
    # 提取对话记录进行存储并一次性返回
    msg_list = []
    messages = state["channel_values"]["messages"]
    for msg in messages:
        # 目前只有纯字符串
        # 后续新增多模态再对content内容进行判断
        msg_list.append(f"【{msg.type}】\n  {msg.content}")
    return msg_list





if __name__ == "__main__":
    from core.memory.connect_db import Postgres_DB
    db = Postgres_DB()
    db.open_db()

    conn = db.conn
    checkpointer = PostgresSaver(conn)
    thread_id = "test"
    msg_list = get_short_memory(checkpointer=checkpointer,thread_id=thread_id)
    print(msg_list)

    db.close_db()




