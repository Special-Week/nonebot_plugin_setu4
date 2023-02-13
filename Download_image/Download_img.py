import asyncio
import os
import sqlite3
import random
from httpx import AsyncClient
from loguru import logger

# 此脚本用来提取sqlite数据库全部链接, 下载图片使用
# sqlite数据库需要放在此脚本同一目录下
# 数据库链接 "https://github.com/Special-Week/nonebot_plugin_setu4/blob/main/nonebot_plugin_setu4/resource/lolicon.db"
# 依赖第三方库httpx以及loguru, 缺失依赖报错no module可通过pip install httpx loguru安装依赖
# 不会重复下载已经有了的图片文件, 只会下载img文件夹内没有的图片
# 学习多任务使用, 请勿大规模爬取代理, 一次性爬取太多可能ip会被ban


async def star_download(url, sem, file_name):
    async with sem:                                                             # 限制最大并发
        try:
            async with AsyncClient() as client:
                re = await client.get(url=url, timeout=120)                     # 下载图片, 超时120秒则异常
                if re.status_code == 200:                                       # 判断状态码, 返回值200就说明拿到了图片, 进行保存
                    with open(f'img/{file_name}', 'wb')as f:
                        f.write(re.content)
                    logger.success(f'下载完成 {file_name}')
                else:                                                           # 状态码非200, 说明有异常, 比如404, log输出可以看到
                    logger.error(f'下载失败 {file_name}, 状态码: {re.status_code}')
                    with open('error.txt', 'a') as f:
                        f.write(
                            f'{file_name}\tstatus_code: {re.status_code}\n')    # 在error.txt文件中记录错误信息

        except:                                                                 # 有异常, 比如超时, log输出可以看到
            logger.error(f'下载失败 {file_name},请求超时')
            # error追加进文件:
            with open('error.txt', 'a') as f:
                f.write(f'{file_name}\t请求超时\n')                              # 在error.txt文件中记录错误信息


async def main():
    conn = sqlite3.connect('lolicon.db')                                        # 连接sqlite数据库文件, 同一级目录下的lolicon.db文件, 请从上面的注释处下载
    cur = conn.cursor()
    logger.info('数据库连接成功')
    cursor = cur.execute("SELECT urls from main where status!='unavailable'")                               # sql提取所有链接
    cursor = cursor.fetchall()
    random.shuffle(cursor)                                                      # 无意义的打乱
    task_list = []                                                              # 任务列表
    sem = asyncio.Semaphore(20)                                                 # 设置并发数20
    for row in cursor:
        url = row[0]                                                            # 提取url
        file_name = url.split('/')[-1]                                          # 文件名
        if not os.path.exists(f'img/{file_name}'):                              # 判断有没有下过, 有这个文件的话就不加入任务
            task = asyncio.create_task(star_download(url, sem, file_name))      # 创建任务
            task_list.append(task)                                              # 添加列表
    logger.info(f'读取到 {len(task_list)} 个图片未下载，准备下载')
    await asyncio.gather(*task_list)                                            # 并发开始跑


if __name__ == '__main__':
    try:
        logger.debug('创建img文件夹')
        os.mkdir('img')
    except:
        logger.debug('文件夹已存在')
        pass
    asyncio.run(main())
