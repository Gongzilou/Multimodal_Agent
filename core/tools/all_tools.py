# 获取所有工具

import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).parent.parent.parent
    )
)





from core.tools import weather
from utils.logger import log


def get_all_tools():

    tool_list = [
        weather.get_weather,
    ]

    log.info(f"当前拥有工具数量:{len(tool_list)}\n{tool_list}")
    return tool_list

# tool_list = get_all_tools()

