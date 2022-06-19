# nonebot_plugin_setu4

内置数据库的setu插件, 另外尝试降低因为风控发不出图的概率(随机修改左上角一颗像素点)

目前数据库共49119条记录

安装方式:

    pip install nonebot_plugin_setu4
    
    nb plugin install nonebot-plugin-setu4

## env 配置项

>以下配置项均可不填，插件会按照默认值读取
>带有*标识的设置项可在指定群聊被setu_perm_cfg.json中的内容覆盖

|config             |type            |default    |example                                              |usage                                   |
|-------------------|----------------|-----------|-----------------------------------------------------|----------------------------------------|
|setu_perm_cfg_path |str             |see example|setu_perm_cfg = './data/setu4'                       |会话(群号或QQ号)启用、r18及其他独立配置项  |
|setu_cd*           |int             |20         |setu_cd = 30                                         |setu通用cd, 为0时无cd                    |
|setu_withdraw_time*|int             |100        |setu_withdraw_time = 30                              |setu通用撤回时间(最大为100秒), 为0时不撤回 |
|setu_max_num*      |int             |10         |setu_max_num = 20                                    |setu一次性最大数量(最小为1)               |
|setu_save          |str             |None       |setu_save = './data/setu4/img'                       |setu保存到本地的路径, 留空则不保存至本地   |
|setu_database_path |str             |see example|setu_database_path = 'https://hub.fastgit.xyz/Special-Week/nonebot_plugin_setu4/raw/main/nonebot_plugin_setu4/resource/lolicon.db'|更新使用的数据库的地址，默认为此项目的resource文件夹下|

setu_save保存后下一次调用碰到这个setu会先从这个文件夹中有的文件匹配, 不需要再下载, 先要自己创建好文件夹

一般无需科学上网, 但是先确保一下自己的服务器能否正常访问pixiv.re

## 插件指令

setu命令:

    命令头: setu|色图|涩图|想色色|来份色色|来份色图|想涩涩|多来点|来点色图|来张setu|来张色图|来点色色|色色|涩涩  (任意一个)
    
    张数: 1 2 3 4 ... 张|个|份  (可不填, 默认1)
    
    r18: 填了就是r18, 不填则不是  (私聊生效, 群聊除非add_r18, 不然视为false)
    
    关键词: 任意 (可不填)
    
    参考:   
    
        setu 10张 r18 白丝
        
        setu 10张 白丝
        
        setu r18 白丝
        
        setu 白丝
        
        setu
        
        (空格可去掉)

添加r18:

    add_r18 xxxxx   (xxxx为qq号码或者群聊号码, 当为qq号码时, 该人在任意有你的bot的群都能在群聊触发r18, 当为群号时, 该群任意人都可以触发r18)

撤销r18:

    del_r18 xxxxx

查看r18列表:

    r18名单
