from httpx import AsyncClient
from nonebot import logger
from nonebot.log import logger
import random
import asyncio
import nonebot
import sqlite3
import os
from pathlib import Path
from PIL import Image
from io import BytesIO
error = "Error:"


# save_path,可在env设置, 默认False, 类型bool或str
try:
    save_path = nonebot.get_driver().config.setu_save
    all_file_name = os.listdir(save_path)
except:
    save_path = False
    all_file_name = []


# 本地setu路径,默认在插件目录下的resource/img
# img_path = str(Path(os.path.join(os.path.dirname(__file__), "resource/img")))
# 读取file_name里面的全部文件名
# all_file_name = os.listdir(img_path)


# 返回列表,内容为setu消息(列表套娃)
async def get_setu(keyword="", r18=False, num=1, quality=75) -> list:
    data = []
    # 连接数据库
    conn = sqlite3.connect(
        Path(os.path.join(os.path.dirname(__file__), "resource")) / "lolicon.db")
    cur = conn.cursor()
    # sql操作,根据keyword和r18进行查询拿到数据
    cursor = cur.execute(
        f"SELECT * from main where (tags like \'%{keyword}%\' or title like \'%{keyword}%\' or author like \'%{keyword}%\') and r18=\'{r18}\'")
    db_data = cursor.fetchall()
    # 断开数据库连接
    conn.close()
    # 如果没有返回结果
    if db_data == []:
        data.append([error, f"图库中没有搜到关于{keyword}的图。", False])
        return data
    # 防止数组越界
    if num > len(db_data):
        num = len(db_data)
    setu_data = random.sample(db_data, num)
    
    async with AsyncClient() as client:
        tasks=[]
        for setu in setu_data:
            tasks.append(pic(setu, quality, client))
        data = await asyncio.gather(*tasks)

    return data


# 返回setu消息列表,内容 [图片, 信息, True/False, url]
async def pic(setu, quality, client):
    setu_title = setu[3]
    setu_url = setu[11].replace('i.pixiv.cat', 'i.pixiv.re')
    setu_pid = setu[0]
    setu_author = setu[4]
    data = (
        "标题:"
        + setu_title
        + "\npid:"
        + str(setu_pid)
        + "\n画师:"
        + setu_author
    )

    logger.info("\n"+data+"\ntags:" +
                setu[8]+"\nR18:"+str(setu[5]))

    # 本地图片如果是用well404的脚本爬的话,就把下面的replace代码解除注释
    file_name = setu_url.split("/")[-1]  # .replace('p', "",1)

    # 判断文件是否本地存在
    if file_name in all_file_name:
        logger.info("图片本地存在")
        image = Image.open(save_path + "/" + file_name)
    # 如果没有就down_pic
    else:
        logger.info("图片本地不存在,正在去i.pixiv.re下载")
        content = await down_pic(setu_url, client)
        if type(content) == int:
            return [error, f"图片下载失败", False, setu_url]
        image = Image.open(BytesIO(content))

    pic = await change_pixel(image, quality)
    return [pic, data, True, setu_url]


# 随机修改左上角第一颗像素的颜色,并且返还图片的base64编码
async def change_pixel(image, quality):
    image = image.convert("RGB")
    image.load()[0, 0] = (random.randint(0, 255),
                          random.randint(0, 255), random.randint(0, 255))
    byte_data = BytesIO()
    image.save(byte_data, format="JPEG", quality=quality)
    # pic是的图片的base64编码
    pic = byte_data.getvalue()
    return pic



# 下载图片并且返回content,或者status_code
async def down_pic(url, client):
    headers = {
        "Referer": "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    }
    re = await client.get(url=url, headers=headers, timeout=120)
    if re.status_code == 200:
        logger.success("成功获取图片")
        if save_path:
            file_name = url.split("/")[-1]
            try:
                with open(f"{save_path}/{file_name}", "wb") as f:
                    f.write(re.content)
                all_file_name.append(file_name)
            except Exception as e:
                logger.error(f'图片存储失败: {e}')
        return re.content
    else:
        logger.error(f"获取图片失败: {re.status_code}")
        return re.status_code
