"""  
根据地址获取实时天气
"""
import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).parent.parent.parent.parent
    )
)





from enum import Enum
from typing import Annotated

import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from config.settings import setting
from core.tools.hefeng.get_jwt import get_jwt
from utils.logger import log

# class LangCode(str,Enum):
#     ZH_HANS = "zh-hans" # 简中
#     ZH_HANT = "zh-hant" # 繁中
#     EN = "en" # 英
#     JA = "ja" # 日
#     KO = "ko" # 韩

class Weather_Args(BaseModel):
    longitude : Annotated[
        float,
        Field(
            description="所需位置的经度。十进制，最多支持小数点后两位。例如：120.62"
        )
    ]
    latitude : Annotated[
        float,
        Field(
            description="所需位置的纬度。十进制，最多支持小数点后两位。例如：31.32"
        )
    ]
    localTime : Annotated[
        bool,
        Field(description="是否返回查询地点的本地时间")
    ] = False
    # lang : Annotated[
    #     LangCode,
    #     Field(description="返回语言代码")
    # ] = LangCode.ZH_HANS



@tool(args_schema=Weather_Args)
def get_weather(
    longitude,
    latitude,
    localTime,
    # lang,
):
    """
    根据经纬度查询实时天气。
    本工具返回已经格式化完成的中文天气数据；
    不要重复调用工具，如果获取结果正常，直接整理内容回复用户。
    """


    # 获取动态生成的JWT，用于平台身份验证
    my_jwt = get_jwt()

    # 获取平台提供的独立API地址
    api_host = setting.API_HOST

    # 拼接url：api地址 + 路径参数（经纬度）
    my_url = f'https://{api_host}/weather/v1/current/{latitude}/{longitude}'
    
    # url的查询参数（不传也行，平台本身有默认值）
    params = {
        "localTime" : str(localTime).lower(), # 和风的该字段只接受小写
        # "lang" : lang
    }
    
    # 请求头：存放动态生成的JWT
    my_headers = {
        "Authorization":f"Bearer {my_jwt}"
    }
    
    # 发送请求，返回相应内容
    try:
        response = requests.get(
            url=my_url,
            headers=my_headers,
            params=params,
            # 5s没连上算超时；连上了但是10s没数据返回也算超时
            timeout=(5, 10),
        )

        # 主动抛出4xx、5xx错误到HTTPError
        response.raise_for_status()

        # 将响应数据转成json格式后进行翻译
        data_json = response.json()
        return format_weather(data_json)
    
    except requests.exceptions.ConnectTimeout as e:
        error_msg = "请求超时：无法连接和风天气服务器，请检查网络"
        log.exception(error_msg)
        raise RuntimeError(error_msg) from e
    except requests.exceptions.ReadTimeout as e:
        error_msg = "请求超时：服务器长时间没有返回数据"
        log.exception(error_msg)
        raise RuntimeError(error_msg) from e
    except requests.exceptions.ConnectionError as e:
        error_msg = "连接失败：网络异常、域名错误或服务器无法访问"
        log.exception(error_msg)
        raise RuntimeError(error_msg) from e
    except requests.exceptions.HTTPError as e:
        error_msg = f"接口返回错误状态码：{response.status_code}, 响应：{response.text[:200]}"
        log.exception(error_msg)
        raise RuntimeError(error_msg) from e
    except Exception as e:
        error_msg = f"发生未知错误：{str(e)}"
        log.exception(error_msg)
        raise RuntimeError(error_msg) from e





# 对返回的响应数据进行翻译
def format_weather(data_json:dict):
    # 风向方位
    compass_map = {
        "n": "北风",
        "nne": "北偏东北",
        "ne": "东北风",
        "ene": "东偏东北",
        "e": "东风",
        "ese": "东偏东南",
        "se": "东南风",
        "sse": "南偏东南",
        "s": "南风",
        "ssw": "南偏西南",
        "sw": "西南风",
        "wsw": "西偏西南",
        "w": "西风",
        "wnw": "西偏西北",
        "nw": "西北风",
        "nnw": "北偏西北",
        "none": "无风",
        "vrb": "风向多变"
    }



    # 天气现象
    condition = data_json.get("condition",{})

    # 温度数据
    temperature = data_json.get("temperature",{})

    # 体感温度
    feelsLike = data_json.get("feelsLike",{})

    # 相对湿度，取值范围 [0, 1]
    humidity = data_json.get("humidity")

    # 风的数据
    wind = data_json.get("wind",{})
    # 风向
    direction = wind.get("direction",{})
    # 风速
    speed = wind.get("speed",{})
    # 蒲福风级
    scale = wind.get("scale","未知")

    # 阵风风速
    windGust = data_json.get("windGust",{})

    # 降水数据
    precipitation = data_json.get("precipitation",{})
    # 累计一小时降水量
    amount = precipitation.get("amount",{})
    # 降水强度
    intensity = precipitation.get("intensity",{})
    # 降水类型
    precipitation_type = precipitation.get("type","未知")

    # 海平面气压
    pressure = data_json.get("pressure",{})

    # 能见度
    visibility = data_json.get("visibility",{})

    # 露点温度
    dewPoint = data_json.get("dewPoint",{})

    # 云量，取值范围 [0, 1]
    cloudCover = data_json.get("cloudCover")

    # 紫外线指数，取值范围 [0, 15]
    uvIndex = data_json.get("uvIndex")

    weather_dic = {
        "天气" : condition.get("text","未知"),
        "气温" : f'{temperature.get("value","未知")} {temperature.get("unit","")}',
        "体感温度" : f'{feelsLike.get("value","未知")} {feelsLike.get("unit","")}',
        "湿度" : f'{humidity * 100}%' if humidity is not None else "未知", # 可能是0——极度干燥
        "风向角度" : direction.get("degree","未知"),
        "风向方位" : compass_map.get(direction.get("compass","未知"),"未知"),
        "风速" : f'{speed.get("value","未知")} {speed.get("unit","")}',
        "蒲福风级" : scale,
        "阵风风速" : f'{windGust.get("value","未知")} {windGust.get("unit","")}',
        "累计一小时降水量" : f'{amount.get("value","未知")} {amount.get("unit","")}',
        "降水强度" : f'{intensity.get("value","未知")} {intensity.get("unit","")}',
        "降水类型" : precipitation_type,
        "海平面气压" : f'{pressure.get("value","未知")} {pressure.get("unit","")}',
        "能见度" : f'{visibility.get("value","未知")} {visibility.get("unit","")}',
        "露点温度" : f'{dewPoint.get("value","未知")} {dewPoint.get("unit","")}',
        "云量" : f'{cloudCover * 100}%' if cloudCover is not None else "未知",
        "紫外线指数" : uvIndex if uvIndex is not None else "未知",

    }

    return weather_dic





if __name__ == "__main__":
    result = get_weather.invoke(
        {
            "longitude" : 120.62,
            "latitude" : 31.32,
            # "localTime" : True,
        }
    )
    print(result)