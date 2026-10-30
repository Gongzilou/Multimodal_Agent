# 创建agent

import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).parent.parent
    )
)





from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from core.create_model import local_chat_model
from core.tools.all_tools import get_all_tools
from utils.logger import log

Agent_System_Prompt = """
你的性格：
活泼可爱

你的功能：
1、查询当前或未来的天气信息
2、查询城市基本信息

你要遵循的规则：
1、所有对外输出的信息，**每一条信息都必须标注来源**：来源只能是【某个工具】或者【自身（模型知识）】；
2、当用户请求超出可用工具的能力时，清晰说明限制；不要擅自用不等价的查询替代，必要时先征求用户同意；
3、当查询城市信息会匹配到多个候选结果时，必须先询问用户需要哪一个；
"""


class Create_Agent:

    def __init__(self,checkpointer = None):
        self.model = local_chat_model()
        self.tool_list = get_all_tools()
        try:
            self.agent = create_agent(
                model=self.model,
                checkpointer=checkpointer,
                tools=self.tool_list,
                middleware=[],
                system_prompt=Agent_System_Prompt,
                name="主控Agent",
            )
            log.info(f"Agent初始化成功:{self.agent.name}")
        except Exception as e:
            log.error(f"Agent初始化失败")
            log.error(f"失败原因:\n{e}")
            raise

    def ask(self,query,user_id,thread_id):
        """  
        query:用户的提问
        user_id:区分不同用户
        thread_id:区分不同会话
        """
        response = self.agent.invoke(
            {
                "messages":[
                    HumanMessage(content=query)
                ]
            },
            config = {
                "configurable":{
                    "thread_id":thread_id
                }
            },
            context = {
                "user_id":user_id
            }
        )

        return response["messages"][-1].content





if __name__ == "__main__":

    # 初始化agent（内存记忆版本）
    from langgraph.checkpoint.memory import InMemorySaver
    checkpointer = InMemorySaver()
    agent = Create_Agent(checkpointer=checkpointer)

    # 标识不同用户user_id——用户登入时取得
    user_id = "Gongzi"
    log.info(f"当前用户ID:{user_id}")

    # 标识不同会话thread_id——开启新对话时，由uuid随机生成
    # python版本3.14及以上可以使用uuid7，
    # 优点：时间前缀 + 随机，有序，数据库索引性能好（uuid4无序，索引性能差）
    import uuid
    thread_id = str(uuid.uuid4())
    log.info(f"当前会话ID:{thread_id}")

    print("="*20 + "Agent对话开始(输入exit退出)" + "="*20)
    while True:

        query = input("\n请输入:\n").strip()
        if query.lower() == "exit":
            print("再见")
            break
        if not query:
            continue
        # 实际生成环境中，要提前对user_id、thread_id进行匹配判断，不符合的无法查看当前会话
        answer = agent.ask(
            query=query,
            user_id=user_id,
            thread_id=thread_id,
        )
        print(f"AI:\n{answer}\n")





