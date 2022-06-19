import os
import random
import time
from pathlib import Path

import nonebot
from nonebot.log import logger

from .resource.setu_message import setu_sendcd

try:
    import ujson as json
except:
    logger.warning('ujson not find, import json instead')
    import json



'''{
    'group_114':{
        'last'     : 114514, # 最后一次发送setu的时间
        'cd'       : 30,     # cd时长
        'r18'      : True,   # r18开关
        'withdraw' : 100,    # 撤回延时
        'maxnum'   : 10      # 单次最高张数
    }
}'''


class PermissionManager:
    def __init__(self) -> None:
        # 读取全局变量
        try: 
            self.setu_perm_cfg_path = str(Path(nonebot.get_driver().config.setu_perm_cfg_path,'setu_perm_cfg.json'))
        except:
            self.setu_perm_cfg_path = 'data/setu4/setu_perm_cfg.json'
        try: 
            self.setu_cd            = int(nonebot.get_driver().config.setu_cd)
        except:
            self.setu_cd            = 30
        try: 
            self.setu_withdraw_time = int(nonebot.get_driver().config.setu_withdraw_time) if int(nonebot.get_driver().config.setu_withdraw_time)<100 else 100
        except:
            self.setu_withdraw_time = 100
        try: 
            self.setu_max_num       = int(nonebot.get_driver().config.setu_max_num)
        except:
            self.setu_withdraw_time = 10
        # 读取perm_cfg
        self.ReadCfg()
    
    # --------------- 文件读写 开始 ---------------
    # 读取cfg
    def ReadCfg(self):
        try:
            # 尝试读取
            with open(self.setu_perm_cfg_path,'r') as f:
                self.cfg = json.loads(f)
        except:
            # 读取失败
            self.cfg = {}
            self.WriteCfg()
    
    # 写入cfg
    def WriteCfg(self):
        # 尝试创建路径
        os.makedirs(self.setu_perm_cfg_path[:-18],mode=0o777,exist_ok=True)
        # 写入数据
        with open(self.setu_perm_cfg_path,'w',encoding='utf-8') as f:
            f.write(json.dumps(self.cfg))
    # --------------- 文件读写 开始 ---------------
    
    # --------------- 查询系统 开始 ---------------
    # 查询sessionId
    def ReadSessionId(self,sessionId):
        try:
            return self.cfg[sessionId]
        except KeyError:
            return False
    
    # 查询上一次发送时间
    def ReadLastSend(self,sessionId):
        try:
            return self.cfg[sessionId]['last']
        except KeyError:
            return 0

    # 查询cd
    def ReadCd(self,sessionId):
        try:
            return self.cfg[sessionId]['cd']
        except KeyError:
            return self.setu_cd
    
    # 查询撤回时间
    def ReadWithdrawTime(self,sessionId):
        try:
            return self.cfg[sessionId]['withdraw']
        except KeyError:
            return self.setu_withdraw_time

    # 查询最大张数
    def ReadMaxNum(self,sessionId):
        try:
            return self.cfg[sessionId]['maxnum']
        except KeyError:
            return self.setu_max_num

    # 查询r18
    def ReadR18(self,sessionId):
        try:
            return self.cfg[sessionId]['r18']
        except KeyError:
            return False
    # --------------- 查询系统 结束 ---------------
    
    # --------------- 逻辑判断 开始 ---------------
    # 查询权限, 并返回修正过的参数
    def CheckPermission(self,sessionId:str,r18flag:bool,num:int,su:bool=False):
        """查询权限, 并返回修正过的参数

        Args:
            sessionId (str): [会话信息]
            r18flag (bool): [是否开启r18]
            num (int): [需求张数]
            su (bool, optional): [是否为管理员]. Defaults to False.

        Raises:
            PermissionError: [未在白名单]
            PermissionError: [cd时间未到]

        Returns:
            [bool, int, int]: [r18是否启用, 图片张数, 撤回时间]
        """
        if not su:
            # 如果会话本身未在名单中, 不启用功能        
            if not self.ReadSessionId(sessionId):
                raise PermissionError('涩图功能已在此会话中禁用！')

            # 查询冷却时间
            timeLeft = self.ReadCd(sessionId) + self.ReadLastSend(sessionId) - time.time()
            if timeLeft > 0:
                hours, minutes, seconds = 0, 0, 0
                if timeLeft >= 60:
                    minutes, seconds = divmod(timeLeft, 60)
                    hours, minutes = divmod(minutes, 60)
                else:
                    seconds = timeLeft
                cd_msg = f"{str(hours) + '小时' if hours else ''}{str(minutes) + '分钟' if minutes else ''}{str(seconds) + '秒' if seconds else ''}"
                raise PermissionError(f"{random.choice(setu_sendcd)} 你的CD还有{cd_msg}")
        
        # 检查r18权限, 图片张数, 撤回时间
        r18  = True if r18flag and self.ReadR18(sessionId) else False
        num_ = num  if num  <=  self.ReadMaxNum(sessionId) else self.ReadMaxNum(sessionId)
        return r18, num_, self.ReadWithdrawTime(sessionId)
    # --------------- 逻辑判断 结束 ---------------

    # --------------- 冷却更新 开始 ---------------
    def UpdateCd(self,sessionId):
        try:
            self.cfg[sessionId]['last'] = time.time()
        except KeyError:
            pass
    # --------------- 冷却更新 结束 ---------------
        
        

