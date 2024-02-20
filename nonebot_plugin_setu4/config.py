from pathlib import Path
from typing import List, Optional, Union

from loguru import logger
from nonebot import get_driver
from pydantic import BaseModel, parse_obj_as

DATA_PATH = Path("data/setu4")
if not DATA_PATH.exists() or not DATA_PATH.is_dir():
    logger.warning(f"数据目录 {DATA_PATH} 不存在, 将自动创建")
    DATA_PATH.mkdir(0o755, parents=True, exist_ok=True)


class Config(BaseModel):
    setu_disable_wlist: bool = False  # 是否禁用白名单检查
    setu_enable_private: bool = False  # 是否允许未在白名单的私聊会话使用
    setu_save: Union[
        bool, str
    ] = False  # 保存图片的路径, 默认False, 填.env时候希望收到的是字符串而不是True
    # 数据库路径, 默认使用github的地址
    database_path: str = "https://raw.githubusercontent.com/Special-Week/nonebot_plugin_setu4/main/nonebot_plugin_setu4/resource/lolicon.db"

    setu_cd: int = 30  # 冷却时间
    setu_withdraw_time: int = 100  # 撤回时间
    setu_max_num: int = 10  # 最大数量
    group_forward_msg: bool = False  # 是否合并转发

    setu_nsfw_path: Union[bool, str] = False
    setu_sfw_path: Union[bool, str] = False
    scientific_agency: Optional[str] = None  # 科学上网代理地址
    setu_quality: List[int] = [5, 75]
    sfw_withdraw: bool = True


config = parse_obj_as(Config, get_driver().config.dict())

# 规范取值范围
config.setu_cd = max(0, config.setu_cd)  # setu_cd不能小于0
config.setu_withdraw_time = max(
    0, config.setu_withdraw_time
)  # 撤回时间不能小于0, 大于100
config.setu_withdraw_time = min(100, config.setu_withdraw_time)
config.setu_max_num = max(1, config.setu_max_num)  # setu_max_num不能大于1小于25
config.setu_max_num = min(25, config.setu_max_num)


config.setu_nsfw_path = (
    f"{config.setu_save}/nsfw" if isinstance(config.setu_save, str) else False
)  # nsfw保存路径
config.setu_sfw_path = (
    f"{config.setu_save}/sfw" if isinstance(config.setu_save, str) else False
)  # sfw保存路径


try:
    if isinstance(config.setu_nsfw_path, str):
        Path(config.setu_nsfw_path).mkdir(0o755, parents=True, exist_ok=True)
    if isinstance(config.setu_sfw_path, str):
        Path(config.setu_sfw_path).mkdir(0o755, parents=True, exist_ok=True)
except Exception as e:
    logger.error(f"创建文件夹失败: {repr(e)}")
    config.setu_nsfw_path = False
    config.setu_sfw_path = False
    config.setu_save = False
