# 创建模型

import sys
from pathlib import Path
sys.path.append(
    str(
        Path(__file__).parent.parent
    )
)





from langchain.chat_models import init_chat_model
from config.settings import setting
from utils.logger import log

# 创建本地chat模型
def local_chat_model():

    try:
        model = init_chat_model(
            model=setting.OLLAMA_CHAT_MODEL1,
            model_provider=setting.OLLAMA_MODEL_PROVIDER,
        )
        log.info(f"Chat模型初始化成功:{setting.OLLAMA_CHAT_MODEL1}")
    except Exception as e:
        log.error(f"Chat模型初始化失败:{setting.OLLAMA_CHAT_MODEL1}")
        log.error(f"失败原因:\n{e}")
        raise

    return model





if __name__ == "__main__":

    model = local_chat_model()

    # from unittest.mock import patch
    # with patch.object(
    #     sys.modules[__name__],
    #     "init_chat_model", 
    #     side_effect=RuntimeError("模拟【模型】初始化失败")
    # ):
    #     model = local_chat_model()