""" 
获取所有工具 
"""
import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).parent.parent.parent
    )
)





from core.tools.hefeng.tool_city import tool_city
from core.tools.hefeng.tool_weather import tool_weather
from utils.logger import log


def get_all_tools():

    # 将创建好的工具注册进来（后续有新增工具也要加进来）
    tool_list = [
        tool_weather,
        tool_city,
    ]

    log.info(f"当前拥有工具数量:{len(tool_list)}")
    return tool_list





if __name__ == "__main__":

    get_all_tools()
