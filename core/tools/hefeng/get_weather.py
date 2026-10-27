"""  
根据经纬度以及时间颗粒度查询当前或未来天气情况
"""
import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).parent.parent.parent.parent
    )
)





import requests

from config.settings import setting
from core.tools.hefeng.get_jwt import get_jwt
from utils.logger import log
from typing import Literal


def request_get_weather(
        longitude: float, 
        latitude: float, 
        granularity: Literal["current","daily","hourly"],
        days: int | None = None, # 查询每日天气需要
        hours: int | None = None, # 查询小时天气需要
):

    """  
    longitude: 经度
    latitude: 纬度
    granularity: 时间颗粒度
        current: 实时天气
        daily: 每日天气
        hourly: 小时天气
    """

    # 获取动态生成的JWT，用于平台身份验证
    my_jwt = get_jwt()

    # 获取平台提供的独立API地址
    api_host = setting.API_HOST

    # 拼接url：api地址 + 路径参数（经纬度）
    my_url = f'https://{api_host}/weather/v1/{granularity}/{latitude}/{longitude}'
    
    # url的查询参数
    # 不直接传None，做判断来传，防止模型乱传。比如颗粒度是current，却加上了days参数
    params = {}
    if granularity == "daily":
        params["days"] = days
    if granularity == "hourly":
        params["hours"] = hours
    
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

        # 将响应数据转成json格式进行返回
        return response.json()
    
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





if __name__ == "__main__":
    result = request_get_weather(
        longitude=120.62,
        latitude=31.32,
        # longitude=77.0,
        # latitude=38.9,
        # granularity="daily",
        # days=2,
        # hours=2,
    )

    print(result)