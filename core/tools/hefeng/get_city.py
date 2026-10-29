"""  
根据城市的名称、Locationid或者经纬度(以英文逗号分割,十进制),
查询城市基本信息
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


def request_get_city(location: str,adm: str = None):
    """  
    location:要查询地区的名称、Locationid或者经纬度(以英文逗号分割,十进制),例如 location=101010100 或 location=116.41,39.92
    
    adm:城市的上级行政区划，可设定只在某个行政区划范围内进行搜索，用于排除重名城市或对结果进行过滤。例如 adm=北京
    """
    # 动态密钥
    my_jwt = get_jwt()
    
    # API_HOST
    my_api_host = setting.API_HOST
    
    # 请求头
    my_headers = {
        "Authorization" : f"Bearer {my_jwt}"
    }
    
    # 请求地址
    my_url = f"https://{my_api_host}/geo/v2/city/lookup"
    
    # 查询参数
    my_params = {
        "location" : location,
        "adm" : adm
    }

    # 发送请求获取响应
    try:
        response = requests.get(
            url=my_url,
            params=my_params,
            headers=my_headers,
            timeout=(5,10)
        )
        # 抛出HTTP异常状态（4xx、5xx）
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP状态异常:{response.status_code}, 响应:\n{response.text[:200]}"
        log.exception(error_msg)
        raise RuntimeError(error_msg) from e
    except requests.exceptions.Timeout as e:
        error_msg = f"请求超时:\n{str(e)}"
        log.exception(error_msg)
        raise RuntimeError(error_msg) from e
    except requests.exceptions.ConnectionError as e:
        error_msg = f"请求连接失败:\n{str(e)}"
        log.exception(error_msg)
        raise RuntimeError(error_msg) from e
    except Exception as e:
        error_msg = f"发生未知错误：{str(e)}"
        log.exception(error_msg)
        raise RuntimeError(error_msg) from e




if __name__ == "__main__":
    response = request_get_city(
        location="朝阳",
        # adm="北京",
        # adm="辽宁",
    )

    print(response)