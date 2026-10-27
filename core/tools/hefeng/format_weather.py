"""  
对返回的天气数据进行清洗，
转化为真正交给模型的数据

返回数据会有三种形式的json格式(实时、每日、小时)
"""
import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).parent.parent.parent.parent
    )
)





from datetime import datetime
from zoneinfo import ZoneInfo


# 将utc时间字符串转成北京时间
def format_time(utc_time: str):
    if not utc_time:
        return ""
    real_time = datetime.fromisoformat(utc_time.replace("Z", "+00:00"))
    return real_time.astimezone(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M")



# 返回数据的最小样式就是类似实时天气的json格式，
# 将其中每个参数进行翻译
def format_json(
    data_json: dict,
    weather_time: str, # 实时天气的预报时间直接取当前北京时间
    sunrise: str = "无", # 只有每日天气有日出日落
    sunset: str = "无",
):
    """  
    data_json:数据最小样式——实时天气的json格式,只是会多一些字段
    weather_time:天气预报时间
    sunrise:日出时间
    sunset:日落时间
    """
    
    # 风向方位
    compass_map = {
        "n": "北风",    "nne": "北偏东北",    "ne": "东北风",     "ene": "东偏东北",
        "e": "东风",    "ese": "东偏东南",    "se": "东南风",     "sse": "南偏东南",
        "s": "南风",    "ssw": "南偏西南",    "sw": "西南风",     "wsw": "西偏西南",
        "w": "西风",    "wnw": "西偏西北",    "nw": "西北风",     "nnw": "北偏西北",
        "none": "无风", 
        "vrb": "风向多变"
    }

    # 天气现象
    condition = data_json.get("condition",{})

    # 温度数据（每日天气白天/夜晚都有最高气温和最低气温，字段不一样）
    temperature = data_json.get("temperature")
    temperature_max = data_json.get("temperatureMax")
    temperature_min = data_json.get("temperatureMin")
    # 判断 + 拼接（气温：15℃ 或者 气温：13℃~16℃）
    temp = "未知"
    if temperature_max is not None and temperature_min is not None:
        temp_max = f'{temperature_max.get("value","未知")} {temperature_max.get("unit","")}'
        temp_min = f'{temperature_min.get("value","未知")} {temperature_min.get("unit","")}'
        temp = f'{temp_min} ~ {temp_max}'
        # "气温" : 13℃~16℃
    elif temperature is not None:
        temp = f'{temperature.get("value","未知")} {temperature.get("unit","")}'
        # "气温" : 13℃

    # 体感温度（每日天气没有这个字段）
    feelsLike = data_json.get("feelsLike",{})

    # 相对湿度，取值范围 [0, 1]，不用提前判断，要转百分比
    humidity = data_json.get("humidity")

    # 风的数据
    wind = data_json.get("wind",{})
    # 风向
    direction = wind.get("direction",{})
    # 风速
    speed = wind.get("speed",{})
    # 蒲福风级
    scale = wind.get("scale","未知")

    # 阵风风速（每日天气是windGustMax）
    windGust = data_json.get("windGust",data_json.get("windGustMax",{}))

    # 降水数据
    precipitation = data_json.get("precipitation",{})
    # 累计一小时降水量
    amount = precipitation.get("amount",{})
    # 降水强度（每日天气没有）
    intensity = precipitation.get("intensity",{})
    # 降水类型
    precipitation_type = precipitation.get("type","未知")
    # 降水概率（实时天气没有）
    probability = precipitation.get("probability")

    # 海平面气压（每日天气没有）
    pressure = data_json.get("pressure",{})

    # 能见度（每日天气没有）
    visibility = data_json.get("visibility",{})

    # 露点温度（每日天气没有）
    dewPoint = data_json.get("dewPoint",{})

    # 云量，取值范围 [0, 1]
    cloudCover = data_json.get("cloudCover")

    # 紫外线指数，取值范围 [0, 15]（每日天气里是uvIndexMax，在最外层，不分白天/夜晚，所以自己加进来）
    uvIndex = data_json.get("uvIndex","未知")

    weather_dic = {
        "预报时间":weather_time,
        "天气" : condition.get("text","未知"),
        "气温" : temp,
        "体感温度" : f'{feelsLike.get("value","未知")} {feelsLike.get("unit","")}',
        "湿度" : f'{round(humidity * 100)}%' if humidity is not None else "未知", # 可能是0——极度干燥
        "风向角度" : direction.get("degree","未知"),
        "风向方位" : compass_map.get(direction.get("compass","未知"),"未知"),
        "风速" : f'{speed.get("value","未知")} {speed.get("unit","")}',
        "蒲福风级" : scale,
        "阵风风速" : f'{windGust.get("value","未知")} {windGust.get("unit","")}',
        "降水量" : f'{amount.get("value","未知")} {amount.get("unit","")}',
        "降水强度" : f'{intensity.get("value","未知")} {intensity.get("unit","")}',
        "降水概率" : f'{round(probability * 100)}%' if probability is not None else "未知",
        "降水类型" : precipitation_type,
        "海平面气压" : f'{pressure.get("value","未知")} {pressure.get("unit","")}',
        "能见度" : f'{visibility.get("value","未知")} {visibility.get("unit","")}',
        "露点温度" : f'{dewPoint.get("value","未知")} {dewPoint.get("unit","")}',
        "云量" : f'{round(cloudCover * 100)}%' if cloudCover is not None else "未知",
        "紫外线指数" : uvIndex,
        "日出时间":sunrise,
        "日落时间":sunset,

    }

    return weather_dic



# 对返回的三种格式数据做判断，
# 提取最小json格式——实时天气的json格式，
# 其中，小时天气、每日天气会有多条这种json格式数据，
# 所以把它们存成列表
# 最终：实时天气 = dict；小时天气、每日天气 = [dict1,dict2,...]，对里面的dict进行翻译
def format_datas(datas_json: dict):

    # 小时天气返回的datas_json
    if "hours" in datas_json:
        hours_list = [] # 存每一小时的天气dict
        for data_json in datas_json["hours"]: # 根据用户要求返回多少小时的数据，平台默认24
            t = format_time(data_json["forecastTime"]) # 时间转换
            d = format_json(data_json, weather_time=t) # 翻译
            hours_list.append(d)
        return hours_list

    # 每日天气返回的datas_json（拆成白天 + 夜晚）
    elif "days" in datas_json:
        days_list = []
        for data_json in datas_json["days"]:
            astro = data_json.get("astro", {}) # 太阳和月亮的天文事件，日出日落在这里面
            sr = format_time(astro.get("sunrise", "")) # 日出时间
            ss = format_time(astro.get("sunset", "")) # 日落时间
            date_str = format_time(data_json["forecastStartTime"])[:10] # 预报开始时间，只要当日日期（2001-01-01）

            # 白天
            daytime = data_json["daytime"] # 当地时间 [07:00, 19:00) 的天气情况
            # 每日天气只有最外层一个uvIndexMax，把它加入白天/夜晚的天气数据里
            daytime["uvIndex"] = data_json["uvIndexMax"]
            day_dic = format_json(
                daytime,
                weather_time=f"{date_str} 白天",
                sunrise=sr,
                sunset=ss
            )
            days_list.append(day_dic)

            # 夜间
            nighttime = data_json["nighttime"] # 当地时间 [19:00, 次日07:00) 的天气情况
            nighttime["uvIndex"] = data_json["uvIndexMax"]
            night_dic = format_json(
                nighttime,
                weather_time=f"{date_str} 夜间",
                sunrise=sr,
                sunset=ss
            )
            days_list.append(night_dic)
        return days_list

    # 实时天气返回的datas_json,只有一个data_json
    else:
        # 实时天气没有预报时间，取当前北京时间
        now_time = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M")
        return format_json(datas_json, weather_time=now_time)





if __name__ == "__main__":
    # 1、发请求，得到响应数据
    from core.tools.hefeng.get_weather import request_get_weather
    datas_json = request_get_weather(
        longitude=120.62,
        latitude=31.32,
        # granularity="current",
        # longitude=77.0,
        # latitude=38.9,
        # granularity="daily",
        # days=2,
        granularity="hourly",
        hours=2,
    )
    # 2、对响应数据进行清洗：提取 + 翻译
    model_data = format_datas(datas_json)

    print(f"响应数据：\n{datas_json}")
    print(f"翻译数据：\n{model_data}")


