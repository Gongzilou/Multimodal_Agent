"""  
模型使用的城市工具

只负责将API接口返回的经过清洗之后的数据传给模型
"""
import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).parent.parent.parent.parent
    )
)





from typing import Annotated

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from core.tools.hefeng.format_city import format_json
from core.tools.hefeng.get_city import request_get_city
from utils.logger import log


class City_Args(BaseModel):
    location : Annotated[
        str,
        Field(description="要查询地区的名称、Locationid或者经纬度(以英文逗号分割,十进制),例如 location=北京 或 location=101010100 或 location=116.41,39.92")
    ]

    adm : Annotated[
        str | None,
        Field(description="城市的上级行政区划，可设定只在某个行政区划范围内进行搜索，用于排除重名城市或对结果进行过滤。例如 adm=北京")
    ] = None

@tool(args_schema=City_Args)
def tool_city(**kwargs):
    """  
    根据城市的名称、Locationid或者经纬度(以英文逗号分割,十进制)查询城市的基本信息。
    返回经过清洗翻译的结构化中文城市数据。
    """
    # 1、发送请求获取城市信息
    try:
        response = request_get_city(**kwargs)
        log.info("获取城市请求发送成功")
    except Exception as e:
        error_msg = f"获取城市请求发送失败:\n{str(e)}"
        log.exception(error_msg)
        # raise RuntimeError(error_msg) from e
        return error_msg

    # 2、清洗响应数据
    try:
        result = format_json(response)
        log.info("响应数据清洗完成，即将发送给模型")
    except  Exception as e:
        error_msg = f"响应数据清洗发生错误:\n{str(e)}"
        log.exception(error_msg)
        # raise RuntimeError(error_msg) from e
        return error_msg

    return result





if __name__ == "__main__":

    result = tool_city.invoke(
        {
            "location" : "朝阳",
            # "adm" : "北京",
            # "adm" : "辽宁",
        }
    )
    print(result)


        