"""  
记忆模块

使用PostgresSql数据库存,
对长短期记忆进行持久化存储
"""
import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).parent.parent
    )
)





import psycopg
from langgraph.checkpoint.postgres import PostgresSaver

from config.settings import setting
from utils.logger import log


# 初始化数据库，进行连接和关闭
class Postgres_DB:
    def __init__(self):
        # 数据库地址
        self.postgres_url = setting.POSTGRES_URL
        # 连接通道(每次数据库关闭后要重新赋值为None)
        self.conn = None
        # agent持久化机制(每次数据库关闭后要重新赋值为None)
        self.checkpointer = None

    # 连接
    def open_db(self):
        # 防止重复连接
        if self.conn:
            log.warning("不要重复连接数据库")
            return
        try:
            # 创建连接通道
            # autocommit=True，关闭默认事务，每条SQL直接提交，否则执行self.checkpointer.setup()会报错
            self.conn = psycopg.connect(self.postgres_url,autocommit=True)
            # 创建checkpointer
            self.checkpointer = PostgresSaver(self.conn)
            # 自动创建需要的表
            self.checkpointer.setup()
            log.info("数据库连接成功,已创建checkpointer")
        except Exception as e:
            self.close_db()
            error_msg = f"连接数据库失败:\n{str(e)}"
            log.exception(error_msg)
            raise RuntimeError(error_msg) from e

    # 关闭
    def close_db(self):
        # 防止重复关闭
        if self.conn is None:
            log.warning("不要重复关闭数据库连接")
            return
        try:
            self.conn.close()
            log.info("数据库连接已关闭")
        except Exception as e:
            error_msg = f"数据库连接关闭失败:\n{str(e)}"
            log.exception(error_msg)
            raise RuntimeError(error_msg) from e
        finally:
            self.conn = None
            self.checkpointer = None





# 短期记忆
def short_memory():
    """ 目前使用内存存储 """
    # return InMemorySaver()





# 长期记忆
def long_memory():
    pass





if __name__ == "__main__":
    my_db = Postgres_DB()
    my_db.open_db()
    my_db.close_db()