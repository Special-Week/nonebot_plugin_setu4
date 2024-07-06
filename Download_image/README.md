# 食用方法


### 反代服务器是racknerd一百来块买的一年的服务器, 6T流量别组团来草


## 推荐

- 去nonebot_plugin_setu4/resource文件夹下把数据库复制过来
- 在这个文件夹打开命令行输入
```
python Download_img.py
```
- 即可下载图片
- 注意依赖于sqlite3, httpx, loguru库
- 需要更换代理请找到 
``` python
url = url.replace('i.pixiv.re', 'setu.tencent-sb.link') 
```
这行代码, 将setu.tencent-sb.link换成你想要的反代地址即可 (也可以直接删掉用i.pixiv.re)
