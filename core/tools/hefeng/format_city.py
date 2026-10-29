"""  
将返回的城市信息数据进行清洗，
转化为提交给模型的数据
"""
import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).parent.parent.parent.parent
    )
)





def format_json(datas_json: dict):
    # 可能有多个城市的信息
    citys = []
    
    for city in datas_json["location"]:
        
        # 夏令时参数
        isDst = "未知"
        if city.get("isDst") is not None:
            if city.get("isDst") == "1":
                isDst = True
            if city.get("isDst") == "0":
                isDst = False
        
        # 对单个城市信息结果做翻译
        city_info = {
            "位置名称" : city.get("name","未知"),
            "位置ID" : city.get("id","未知"),
            "纬度" : city.get("lat","未知"),
            "经度" : city.get("lon","未知"),
            "上级行政区划名称" : city.get("adm2","未知"),
            "一级行政区域名称" : city.get("adm1","未知"),
            "国家名称" : city.get("country","未知"),
            "时区" : city.get("tz","未知"),
            "当前位置与UTC时间偏移的小数值" : city.get("utcOffset","未知"),
            "是否处于夏令时" : isDst,
            "位置的属性" : city.get("type","未知"),
            "位置的评分" : city.get("rank","未知"),
        }

        citys.append(city_info)

    return citys





if __name__ == "__main__":

    from core.tools.hefeng.get_city import request_get_city
    response = request_get_city(
        location="朝阳",
        # adm="北京",
        # adm="辽宁",
    )

    result = format_json(response)

    print(result)