import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).parent.parent
    )
)





from utils.logger import log

log.info(f"本文档路径为：{__file__}")


