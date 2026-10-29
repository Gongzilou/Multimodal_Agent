"""  
模型使用的天气工具

只负责将API接口返回的经过清洗之后的数据传给模型
"""
import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).parent.parent.parent.parent
    )
)





from typing import Annotated, Literal

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from core.tools.hefeng.format_weather import format_datas
from core.tools.hefeng.get_weather import request_get_weather
from utils.logger import log


class Weather_Args(BaseModel):
    longitude : Annotated[float,Field(description="所需位置的经度。十进制，最多支持小数点后两位。例如 116.41")]
    latitude : Annotated[float,Field(description="所需位置的纬度。十进制，最多支持小数点后两位。例如 39.92")]
    granularity : Annotated[
        Literal["current","daily","hourly"],
        Field(description="时间颗粒度。枚举类型，current表示实时查询；daily表示按天查询；hourly表示按小时查询")
    ]
    days : Annotated[int | None,Field(description="预报天数，支持1-10天，默认值为None",ge=1,le=10)] = None
    hours : Annotated[int | None,Field(description="预报小时数，支持1-240小时，默认值为None",ge=1,le=240)] = None

@tool(args_schema=Weather_Args)
def tool_weather(**kwargs):
    """
    根据地理位置的经纬度以及时间颗粒度查询当前或未来的天气情况。
    支持实时查询current、按天查询daily、按小时查询hourly。
    - current：实时天气，不需要days/hours
    - daily：逐日预报，最多支持10天
    - hourly：逐小时预报，最多支持240小时
    返回经过清洗翻译的结构化中文天气数据。
    说明：格点实时数据短时间会存在小幅正常波动；逐日预报缺少体感温度、海平面气压、露点、能见度、降水强度字段，对应值为“未知”。
    """
    # 1、发送请求获取响应数据
    try:
        response_json = request_get_weather(**kwargs)
        log.info("获取天气请求发送成功")
    except Exception as e:
        error_msg = f"获取天气请求发送失败:\n{str(e)}"
        log.exception(error_msg)
        # raise RuntimeError(error_msg) from e
        return error_msg

    # 2、将响应数据进行清洗：提取 + 翻译
    try:
        result = format_datas(response_json)
        log.info("响应数据清洗完成，即将发送给模型")
    except  Exception as e:
        error_msg = f"响应数据清洗发生错误:\n{str(e)}"
        log.exception(error_msg)
        # raise RuntimeError(error_msg) from e
        return error_msg

    return result





if __name__ == "__main__":
    result = tool_weather.invoke(
        {
            # "longitude" : 77.0, # 华盛顿
            # "latitude" : 38.9,
            "longitude" : 120.62, # 苏州
            "latitude" : 31.32,
            # "granularity" : "current",

            "granularity" : "daily",
            "days" : 2,

            # "granularity" : "hourly",
            # "hours" : 2,
        }
    )
    print(result)