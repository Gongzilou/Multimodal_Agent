# 添加根路径到系统路径列表中
import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).parent.parent
    )
)





import os

from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 获取系统环境变量
class Setting: 
    # ==============================Log==============================
    # ==============================Log==============================
    # ==============================Log==============================
    # logger等级
    LOG_LEVEL = os.getenv("LOG_LEVEL")
    # logger存储位置
    LOG_FOLDER_PATH = os.getenv("LOG_FOLDER_PATH")

    # ==============================Model==============================
    # ==============================Model==============================
    # ==============================Model==============================
    # 模型供应商
    OLLAMA_MODEL_PROVIDER = os.getenv("OLLAMA_MODEL_PROVIDER")
    # 主控大脑
    OLLAMA_CHAT_MODEL1 = os.getenv("OLLAMA_CHAT_MODEL1")
    # 备用大脑
    OLLAMA_CHAT_MODEL2 = os.getenv("OLLAMA_CHAT_MODEL2")

    # ==============================Tool==============================
    # ==============================Tool==============================
    # ==============================Tool==============================
    # 1、weather
    # 密钥对存放路径
    KEYS_FOLDER_PATH = os.getenv("KEYS_FOLDER_PATH")
    # 创建时的开发者ID
    ISS = os.getenv("ISS")
    # 创建时的独立API地址
    API_HOST = os.getenv("API_HOST")
    # 创建时的项目ID
    SUB = os.getenv("SUB")
    # 创建时的凭据ID
    KID = os.getenv("KID")

    # ==============================PostgresSql==============================
    # ==============================PostgresSql==============================
    # ==============================PostgresSql==============================
    POSTGRES_URL = os.getenv("POSTGRES_URL")





# 直接实例化，方便后续调用
setting = Setting()





if __name__ == "__main__":
    try:
        setting = Setting()
        print(f"已成功获取环境变量:\n{setting.OLLAMA_CHAT_MODEL1}\n{setting.OLLAMA_CHAT_MODEL2}")
    except Exception as e:
        print(f"获取环境变量失败：{e}")
