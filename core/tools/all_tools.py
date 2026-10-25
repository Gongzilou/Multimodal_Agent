# 获取所有工具

import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).parent.parent.parent
    )
)





from pathlib import Path

from core.tools import weather
from utils.logger import log


# 遍历tools目录，获取所有已创建工具
# 在下方注册工具时做判断，防止创建了工具但忘记注册
def check_tools():
    # 所有工具所在目录
    tools_folder_path = "core/tools"
    tools = []
    # 只遍历tools层，不需要rglob()递归遍历子目录
    for f in Path(tools_folder_path).glob("*.py"):
        # all_tools.py不是工具
        if f.is_file() and f.stem != "all_tools":
            tools.append(f.stem)
    return tools



def get_all_tools():

    # 将创建好的工具注册进来（后续有新增工具也要加进来）
    tool_list = [
        weather.get_weather,
    ]

    # 判断是否有遗漏注册的工具
    if len(tool_list) != len(check_tools()):
        log.warning("当前尚有工具未注册，请检查！")

    log.info(f"当前拥有工具数量:{len(tool_list)}")
    return tool_list





if __name__ == "__main__":

    print("已创建工具：")
    for tool in check_tools():
        print(tool)
