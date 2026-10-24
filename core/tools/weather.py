# 天气工具

from langchain_core.tools import tool


@tool
def get_weather(city: str = "苏州") -> dict:
    """获取指定城市的天气
    如果用户没有说明具体城市，直接使用默认城市【苏州】，不要追问用户
    Args:
        city: 需要查询天气的城市名称
    """
    return {city: "晴空万里"}
