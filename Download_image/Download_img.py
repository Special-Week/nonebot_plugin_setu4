"""下载图片"""
import asyncio
import json
import os
import random
import sqlite3

from httpx import AsyncClient
from loguru import logger


class DownloadImg:
    def __init__(self) -> None:
        """
        初始化数据库连接, 创建img文件夹, 初始化数据
        """

        self.cur = sqlite3.connect("lolicon.db").cursor()
        logger.info("数据库连接成功")
        try:
            logger.info("创建img文件夹")
            os.mkdir("img")
            os.mkdir("img/nsfw")
            os.mkdir("img/sfw")
        except Exception:
            logger.debug("文件夹已存在")
        self.data: list = self.cur.execute(
            "SELECT urls,r18 from main where status!='unavailable'"
        ).fetchall()
        random.shuffle(self.data)
        self.error_json = {}

    async def main(self) -> None:
        """
        主函数, 发起下载任务
        """

        task_list = []
        sem = asyncio.Semaphore(30)
        for item in self.data:
            url: str = item[0]
            file_name = url.split("/")[-1]
            r18: int = item[1]  # 0, 1
            if (not os.path.exists(f"img/nsfw/{file_name}")) and (
                not os.path.exists(f"img/sfw/{file_name}")
            ):
                task_list.append(self.start_download(url, file_name, sem, r18))
        logger.info(f"读取到 {len(task_list)} 个图片未下载，准备下载")
        await asyncio.gather(*task_list)

    async def start_download(
        self, url: str, file_name: str, sem: asyncio.Semaphore, r18: int
    ):
        """
        下载图片
        """

        url = url.replace("i.pixiv.re", "setu.woshishaluan.top")  # 反代地址
        save_path = f"img/nsfw/{file_name}" if r18 else f"img/sfw/{file_name}"
        async with sem:
            try:
                async with AsyncClient() as client:
                    re = await client.get(url=url, timeout=120)
                    if re.status_code == 200:
                        with open(save_path, "wb") as f:
                            f.write(re.content)
                        logger.success(f"下载完成 {file_name}")
                    else:
                        logger.error(f"下载失败 {file_name}, 状态码: {re.status_code}")
                        if re.status_code not in self.error_json:
                            self.error_json.update({re.status_code: []})
                        self.error_json[re.status_code].append(url)
                        self.save_error()

            except Exception as e:
                logger.error(f"下载失败 {file_name},请求超时")
                if str(e) not in self.error_json:
                    self.error_json.update({str(e): []})
                self.error_json[str(e)].append(url)
                self.save_error()

    def save_error(self):
        """
        保存错误信息
        """
        
        with open("error.json", "w", encoding="utf-8") as f:
            json.dump(self.error_json, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    download = DownloadImg()
    asyncio.run(download.main())
