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
    # 主控大脑
    OLLAMA_CHAT_MODEL1 = os.getenv("OLLAMA_CHAT_MODEL1")
    # 备用大脑
    OLLAMA_CHAT_MODEL2 = os.getenv("OLLAMA_CHAT_MODEL2")

# 直接实例化，方便后续调用
setting = Setting()





if __name__ == "__main__":
    try:
        setting = Setting()
        print(f"已成功获取环境变量:\n{setting.OLLAMA_CHAT_MODEL1}\n{setting.OLLAMA_CHAT_MODEL2}")
    except Exception as e:
        print(f"获取环境变量失败：{e}")
