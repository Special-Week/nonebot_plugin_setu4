import asyncio
import os
import random
from re import I, sub

import nonebot
from nonebot import on_command, on_regex
from nonebot.adapters.onebot.v11 import (GROUP, PRIVATE_FRIEND, Bot,
                                         GroupMessageEvent, Message,
                                         MessageEvent, MessageSegment,
                                         PrivateMessageEvent)
from nonebot.exception import ActionFailed
from nonebot.log import logger
from nonebot.params import CommandArg, State
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State

from .get_data import get_setu
from .json_manager import read_json, remove_json, to_json, write_json
from .setu_message import setu_sendcd, setu_sendmessage

# setu cd,可在env设置,默认20s,类型int
try:
    cdTime = nonebot.get_driver().config.setu_cd
except:
    cdTime = 20

# setu_ban名单,可在env设置,类型string列表
try:
    banlist = nonebot.get_driver().config.setu_ban
except:
    banlist = []

# 撤回时间,可在env设置,默认100s,类型int
try:
    withdraw_time = nonebot.get_driver().config.setu_withdraw_time
except:
    withdraw_time = 100

# 一次最大多少张图片,可在env设置,默认10张,类型int
try:
    max_num = nonebot.get_driver().config.setu_max_num
except:
    max_num = 10


# 先读一读试试
try:
    fp = open('data/setu4/r18list.txt')
    fp.close()
# 没有的话咱就新建
except:
    # 尝试新建data文件夹
    try:
        os.makedirs('data/setu4')
    except FileExistsError:
        logger.info('data/setu4文件夹已存在')
    except Exception as e:
        raise Exception(f'无法新建data/setu4文件夹, 请检查您的工作路径及读写权限!\n{e}')
    fp = open('data/setu4/r18list.txt', 'w')
    fp.write("114514\n")
    fp.close()

# 正则部分
setu = on_regex(
    r"^(setu|色图|涩图|想色色|来份色色|来份色图|想涩涩|多来点|来点色图|来张setu|来张色图|来点色色|色色|涩涩)\s?([x|✖️|×|X|*]?\d+[张|个|份]?)?\s?(r18)?\s?(.*)?",
    flags=I,
    permission=PRIVATE_FRIEND | GROUP,
    priority=10,
    block=True
)


# 响应器处理操作
@setu.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State = State()):
    global mid
    args = list(state["_matched_groups"])
    r18flag = args[2]
    key = args[3]
    key = sub('[\'\"]', '', key)  # 去掉引号防止sql注入
    num = args[1]
    num = int(sub(r"[张|个|份|x|✖️|×|X|*]", "", num)) if num else 1

    if num > max_num or num < 1:
        await setu.finish(f"数量需要在1-{max_num}之间")

    # 色图图片质量, 如果num为3-6质量为70,如果num为7-max质量为50,其余为90(图片质量太高发起来太费时间了)
    if num >= 3 and num <= 6:
        quality = 70
    elif num >= 7:
        quality = 50
    else:
        quality = 90

    if num >=3:
        await setu.send(f"由于数量过多请等待\n当前图片质量为{quality}\n3-6:quality = 70\n7-{max_num}:quality = 50")



    qid = event.get_user_id()
    mid = event.message_id
    sid = event.get_session_id()
    # 判断该群聊setu功能是否被禁用
    for session_id in banlist:
        if str(session_id) in sid:
            await setu.finish("涩图功能已在此会话中禁用！")
    data = read_json()
    try:
        cd = event.time - data[qid][0]
    except Exception:
        cd = cdTime + 1

    # 读取r18列表
    r18list = []
    with open('setu4/r18list.txt', 'r') as fp:
        while True:
            line = fp.readline()
            if not line:
                break
            r18list.append(line.strip("\n"))

    # 先判断r18flag和私聊是不是都是True进行赋值
    r18 = True if (isinstance(event, PrivateMessageEvent)
                   and r18flag) else False
    # 如果r18是false的话在进行r18list判断
    if not r18:
        for groubnumber in r18list:
            if groubnumber in sid:
                r18 = (True if (r18flag) else False)

    if key == "":
        flagLog = f"\nR18 == {str(r18)}\nkeyword == NULL\nnum == {num}\n"
    else:
        flagLog = f"\nR18 == {str(r18)}\nkeyword == {key}\nnum == {num}\n"

    logger.info(f"key = {key}\tr18 = {r18}\tnum = {num}")       # 控制台输出

    # cd判断,superusers无视cd
    if (
        cd > cdTime
        or event.get_user_id() in nonebot.get_driver().config.superusers
    ):
        write_json(qid, event.time, mid, data)
        # data是数组套娃, 数组中的每个元素内容为: [图片, 信息, True/False, url]
        data = await get_setu(key, r18, num, quality)

        # 发送的消息列表
        message_list = []
        for pic in data:
            # 如果状态为True,说明图片拿到了
            if pic[2]:
                message = f"{random.choice(setu_sendmessage)}{flagLog}" + \
                    Message(pic[1]) + MessageSegment.image(pic[0])
                message_list.append(message)
            # 状态为false的消息,图片没拿到
            else:
                message = pic[0] + pic[1]
                message_list.append(message)

        # 为后面撤回消息做准备
        setu_msg_id = []
        # 尝试发送
        try:
            if isinstance(event, PrivateMessageEvent):
                # 私聊直接发送
                for msg in message_list:
                    setu_msg_id.append((await setu.send(msg))['message_id'])    # 我超这串代码好丑啊
            elif isinstance(event, GroupMessageEvent):
                # 群聊以转发消息的方式发送
                msgs = [to_json(msg, "setu-bot", bot.self_id)
                        for msg in message_list]
                setu_msg_id.append((await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=msgs))['message_id'])

        # 发送失败
        except ActionFailed as e:
            logger.warning(e)
            remove_json(qid)
            await setu.finish(
                message=Message(f"消息被风控了捏，图发不出来，请尽量减少发送的图片数量"),
                at_sender=True,
            )

    # cd还没过的情况
    else:
        time_last = cdTime - cd
        hours, minutes, seconds = 0, 0, 0
        if time_last >= 60:
            minutes, seconds = divmod(time_last, 60)
            hours, minutes = divmod(minutes, 60)
        else:
            seconds = time_last
        cd_msg = f"{str(hours) + '小时' if hours else ''}{str(minutes) + '分钟' if minutes else ''}{str(seconds) + '秒' if seconds else ''}"

        await setu.send(f"{random.choice(setu_sendcd)} 你的CD还有{cd_msg}", at_sender=True)

     # 自动撤回涩图
    if withdraw_time != 0:
        try:
            await asyncio.sleep(withdraw_time)
            for msg_id in setu_msg_id:
                await bot.delete_msg(message_id=msg_id)
        except:
            pass


# r18列表添加用的,权限SUPERSUSER
addr18list = on_command("add_r18", permission=SUPERUSER, block=True, priority=10)


@addr18list.handle()
async def _(arg: Message = CommandArg()):
    # 获取消息文本
    msg = arg.extract_plain_text().strip().split()[0]
    # 写入文件
    with open("setu4/r18list.txt", "a") as f:
        f.write(msg + "\n")
    await addr18list.finish("ID:"+msg+"添加成功")


# r18列表删除用的,权限SUPERSUSER
del_r18list = on_command("del_r18", permission=SUPERUSER, block=True, priority=10)


@del_r18list.handle()
async def _(arg: Message = CommandArg()):
    # 获取消息文本
    msg = arg.extract_plain_text().strip().split()[0]
    # 写入文件
    with open("setu4/r18list.txt", 'r') as file:
        lines = file.readlines()
        # 找到msg在lines的位置
        for i in range(len(lines)):
            if (msg+'\n') == lines[i]:
                del lines[i]
                break
    with open("setu4/r18list.txt", 'w') as file:
        # 将删除行后的数据写入文件
        file.writelines(lines)

    await del_r18list.finish("ID:"+msg+"删除成功")


get_r18list = on_command("r18名单", permission=SUPERUSER, block=True, priority=10)


@get_r18list.handle()
async def _():
    r18list = []
    with open('setu4/r18list.txt') as fp:
        while True:
            line = fp.readline()
            if not line:
                break
            r18list.append(line.strip("\n"))
    await get_r18list.finish("R18名单：\n" + str(r18list))
