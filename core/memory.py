# 创建长短期记忆

from langgraph.checkpoint.memory import InMemorySaver


# 短期记忆
def short_memory():
    """ 目前使用内存存储 """
    return InMemorySaver()

# 长期记忆
def long_memory():
    pass