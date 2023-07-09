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
url = url.replace('i.pixiv.re', 'setu.woshishaluan.top') 
```
这行代码, 将setu.woshishaluan.top换成你想要的反代地址即可 (也可以直接删掉用i.pixiv.re)


## 懒人
- 直接运行这下面的二进制构建也可下载图片

- 如果用命令行启动用有两个参数可选:

```
-sem(下载的并发量) 
-proxy(代理反代服务器地址, 默认为setu.woshishaluan.top)
```

如果我的服务器不可用了请自行更换
eg: downloadImg_win_x86_64.exe -sem 5 -proxy i.pixiv.re