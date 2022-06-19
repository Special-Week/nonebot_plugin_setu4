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
from .resource.setu_message import setu_sendmessage
from permission_manager import PermissionManager


pm = PermissionManager()

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
    args = list(state["_matched_groups"])
    r18flag = args[2]
    key = args[3]
    key = sub('[\'\"]', '', key)  # 去掉引号防止sql注入
    num = args[1]
    num = int(sub(r"[张|个|份|x|✖️|×|X|*]", "", num)) if num else 1

    # 根据会话类型生成sessionId
    if isinstance(event, PrivateMessageEvent):
        sessionId = 'user_' + str(event.user_id)
    if isinstance(event, GroupMessageEvent):
        sessionId = 'group_' + str(event.group_id)

    # 权限检查
    try:
        r18,num,withdraw_time = pm.CheckPermission(sessionId,su=(str(event.user_id) in nonebot.get_driver().config.superusers))
    except PermissionError as e:
        await setu.finish(e,at_sender=True)


    # 色图图片质量, 如果num为3-6质量为70,如果num为7-max质量为50,其余为90(图片质量太高发起来太费时间了)
    if num >= 3 and num <= 6:
        quality = 70
    elif num >= 7:
        quality = 50
    else:
        quality = 90

    if num >=3:
        await setu.send(f"由于数量过多请等待\n当前图片质量为{quality}\n3-6:quality = 70\n7+:quality = 50")

    # 控制台输出
    if key == "":
        flagLog = f"\nR18 == {str(r18)}\nkeyword == NULL\nnum == {num}\n"
    else:
        flagLog = f"\nR18 == {str(r18)}\nkeyword == {key}\nnum == {num}\n"

    logger.info(f"key = {key}\tr18 = {r18}\tnum = {num}")       # 控制台输出


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
                setu_msg_id.append((await setu.send(msg))['message_id'])
        elif isinstance(event, GroupMessageEvent):
            # 群聊以转发消息的方式发送
            msgs = []
            for msg in message_list:
                msgs.append({
                    'type': 'node',
                    'data': {
                        'name': "setu-bot",
                        'uin': bot.self_id,
                        'content': msg
                    }
                })
            setu_msg_id.append((await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=msgs))['message_id'])

    # 发送失败
    except ActionFailed as e:
        logger.warning(e)
        await setu.finish(
            message=Message(f"消息被风控了捏，图发不出来，请尽量减少发送的图片数量"),
            at_sender=True,
        )


     # 自动撤回涩图
    if withdraw_time != 0:
        try:
            await asyncio.sleep(withdraw_time)
            for msg_id in setu_msg_id:
                await bot.delete_msg(message_id=msg_id)
        except:
            pass


## r18列表添加用的,权限SUPERSUSER
#addr18list = on_command("add_r18", permission=SUPERUSER, block=True, priority=10)
#
#
#@addr18list.handle()
#async def _(arg: Message = CommandArg()):
#    # 获取消息文本
#    msg = arg.extract_plain_text().strip().split()[0]
#    # 写入文件
#    with open("data/setu4/r18list.txt", "a") as f:
#        f.write(msg + "\n")
#    await addr18list.finish("ID:"+msg+"添加成功")
#
#
## r18列表删除用的,权限SUPERSUSER
#del_r18list = on_command("del_r18", permission=SUPERUSER, block=True, priority=10)
#
#
#@del_r18list.handle()
#async def _(arg: Message = CommandArg()):
#    # 获取消息文本
#    msg = arg.extract_plain_text().strip().split()[0]
#    # 写入文件
#    with open("data/setu4/r18list.txt", 'r') as file:
#        lines = file.readlines()
#        # 找到msg在lines的位置
#        for i in range(len(lines)):
#            if (msg+'\n') == lines[i]:
#                del lines[i]
#                break
#    with open("data/setu4/r18list.txt", 'w') as file:
#        # 将删除行后的数据写入文件
#        file.writelines(lines)
#
#    await del_r18list.finish("ID:"+msg+"删除成功")
#
#
#get_r18list = on_command("r18名单", permission=SUPERUSER, block=True, priority=10)
#
#
#@get_r18list.handle()
#async def _():
#    r18list = []
#    with open('data/setu4/r18list.txt') as fp:
#        while True:
#            line = fp.readline()
#            if not line:
#                break
#            r18list.append(line.strip("\n"))
#    await get_r18list.finish("R18名单：\n" + str(r18list))
