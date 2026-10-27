"""  
每次发送请求前,动态生成JWT

JWT = 经过Base64URL编码的 Header + Payload + Signature

其中,
Header:
    {
        "alg": "EdDSA", 签名算法，保持不变
        "kid": "创建时的凭据ID"
    }

Payload
    {
        "iss": "创建时的开发者ID",
        "sub": "创建时的项目ID",
        "iat": JWT签发生效的开始时间,建议为当前时间前30秒,防止误差
        "exp": JWT过期时间,保证这一次生成的JWT有效期多久
    }

Signature:
    将Header和Payload分别进行Base64URL编码并用英文句号拼接在一起,
    然后使用私钥对其进行Ed25519算法的签名,
    之后对签名结果同样进行Base64URL编码
    注意,是Base64URL,不是Base64

最后,将经过Base64URL编码的三者用英文句号拼接,这就是最后的密钥JWT
"""
import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).parent.parent.parent.parent
    )
)





import time

import jwt

from config.settings import setting
from utils.logger import log


def get_jwt():

    # 构造Header、Payload（根据和风天气平台要求填写字段）
    headers = {
        # # 签名算法，这里不写，在下面编码时再写，密码库会自动填充这里
        # "alg":"EdDSA",
        # 创建时的凭据ID
        "kid":setting.KID,
    }

    payload = {
        # 创建时的开发者ID
        "iss":setting.ISS,
        # 创建时的项目ID
        "sub":setting.SUB,
        # JWT签发生效的开始时间,建议为当前时间前30秒,防止误差
        "iat":int(time.time()) - 30,
        # JWT过期时间,保证这一次生成的JWT有效期多久
        "exp":int(time.time()) + 270,
    }

    # 读取本地私钥
    try:
        with open(f"{setting.KEYS_FOLDER_PATH}/private.key", "rb") as f:
            private_key = f.read()
        log.info("已读取本地私钥")
    except Exception as e:
        log.error(f"本地私钥读取失败:\n{e}")
        raise

    # 用ed25519(EdDSA)签名生成jwt
    try:
        my_jwt = jwt.encode(
            # 私钥
            key=private_key,
            headers=headers,
            payload=payload,
            # 告诉PyJWT密码库用的什么签名算法，必须和headers里保持一致，headers不写会自动填充
            algorithm="EdDSA",
        )
        log.info(f"已生成JWT")
        return my_jwt
    except Exception as e:
        log.error(f"JWT生成失败:\n{e}")
        raise
    




if __name__ == "__main__":
    print(get_jwt())