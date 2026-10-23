# 添加根路径到系统路径列表
import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).parent.parent
    )
)





import logging
from datetime import datetime

from config.settings import setting


# 自定义层级化logger（时间-log名称-log等级-log信息）
def get_logger(name: str):
    # 1、先获取新logger
    logger = logging.getLogger(name)

    # 2、判断是否已经配置过handler，防止import时重复配置导致日志重复打印
    if logger.handlers:
        return logger

    # =====3、开始配置handler（两种：终端输出 + 文档存储）=====

    # 设置logger等级
    log_level = getattr(logging,setting.LOG_LEVEL,logging.INFO)
    logger.setLevel(log_level)

    # 设置logger打印样式
    log_structured_output = logging.Formatter(
        fmt="{asctime} - {name} - {levelname} - {message}",
        datefmt="%Y/%m/%d %H:%M:%S",
        style="{"
    )

    # 让logger在终端显示，同时存为文档

    # 终端显示
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_structured_output)

    # 存为文档
    # 先创建路径文件夹，再拼接文档路径
    folder_path = Path(setting.LOG_FOLDER_PATH) # 获取路径
    folder_path.mkdir(parents=True,exist_ok=True) # 创建路径
    log_file_name = f"{folder_path}/{datetime.now():%Y%m%d}.log" # 文档路径 = 文件夹路径 / 文档名
    file_handler = logging.FileHandler(
        filename=log_file_name,
        encoding="utf-8"
    ) # 存储
    file_handler.setFormatter(log_structured_output)



    # 4、将配置完的两个handler加到logger里
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger



# 只配置一次，后面直接使用
log = get_logger("Multimodal_Agent")





if __name__ == "__main__":
    # 能看到哪些，取决于setting的配置
    log.debug("这是DEBUG等级")
    log.info("这是INFO等级")
    log.warning("这是WARNING等级")
    log.error("这是ERROR等级")
    log.critical("这是CRITICAL等级")




    
