"""  
获取密钥对并存放到指定目录的keys文件夹中

只执行一次
"""
import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).parent.parent.parent.parent
    )
)





from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from utils.logger import log
from config.settings import setting

try:
    # 创建密钥对存放的文件夹(weather/keys)
    # folder_path = Path(__file__).parent / "keys"
    folder_path = Path(setting.KEYS_FOLDER_PATH)
    folder_path.mkdir(exist_ok=True)
    log.info(f"密钥对文件夹创建成功:\n{folder_path}")
except Exception as e:
    log.error(f"密钥对文件夹创建失败:\n{e}")
    raise



try:
    # 生成ed25519私钥
    private_key = ed25519.Ed25519PrivateKey.generate()

    # 导出私钥（PEM格式）
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # 存放私钥
    private_path = folder_path / "private.key"
    with open(private_path, "wb") as f:
        f.write(private_pem)
    log.info(f"私钥已生成:\n{private_path}")
except Exception as e:
    log.error(f"私钥生成失败:\n{e}")
    raise



try:
    # 从私钥拿到公钥，导出公钥PEM
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # 存放公钥
    public_path = folder_path / "public.key"
    with open(public_path, "wb") as f:
        f.write(public_pem)
    log.info(f"公钥已生成:\n{public_path}")
except Exception as e:
    log.error(f"公钥生成失败:\n{e}")
    raise


