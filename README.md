# 仓库目前施工中, pypi上目前为青春版
https://github.com/Special-Week/youth-version-of-setu4
# nonebot_plugin_setu4

内置数据库的setu插件, 另外尝试降低因为风控发不出图的概率(随机修改左上角一颗像素点)

目前数据库共49667条记录

安装方式:

    pip install nonebot_plugin_setu4
    
    nb plugin install nonebot-plugin-setu4

## env 配置项

>以下配置项均可不填，插件会按照默认值读取

|config             |type            |default    |example                                  |usage                                   |
|-------------------|----------------|-----------|-----------------------------------------|----------------------------------------|
|setu_enable_private|bool            |False      |setu_enable_private = True               |是否允许未在白名单的私聊会话使用(群聊照样需要指令开启, 看下文)|
|setu_perm_cfg_path |str             |see example|setu_perm_cfg = './data/setu4'           |会话(群号或QQ号)启用、r18及其他独立配置项  |
|setu_save          |str             |None       |setu_save = './data/setu4/img'           |setu保存到本地的路径, 留空则不保存至本地   |
|setu_regex         |str             |see example|setu_save = see description[^1]          |setu插件的正则表达式匹配                  |
|setu_database_path |str             |see example|setu_database_path = see description[^2] |更新使用的数据库的地址, 默认为此项目的resource文件夹下|
|setu_cd*           |int             |20         |setu_cd = 30                             |setu默认cd[0,+∞], 为0时无cd              |
|setu_withdraw_time*|int             |100        |setu_withdraw_time = 30                  |setu默认撤回时间[0,100], 为0时不撤回      |
|setu_max_num*      |int             |10         |setu_max_num = 20                        |setu默认一次性最大数量[1,25]              |

>带有*标识的设置项可在指定群聊被setu_perm_cfg.json中的内容覆盖

[^1]:"^(setu|色图|涩图|想色色|来份色色|来份色图|想涩涩|多来点|来点色图|来张setu|来张色图|来点色色|色色|涩涩)\s?([x|✖️|×|X|*]?\d+[张|个|份]?)?\s?(r18)?\s?(.*)?"

[^2]:'https://github.com/Special-Week/nonebot_plugin_setu4/raw/main/nonebot_plugin_setu4/resource/lolicon.db'

setu_save保存后下一次调用碰到这个setu会先从这个文件夹中进行匹配, 不需要再下载, 需要先要自己创建好文件夹

一般无需科学上网, 但是先确保一下自己的服务器能否正常访问 [pixiv.re](https://pixiv.re)

## 获取setu

    命令头: setu|色图|涩图|想色色|来份色色|来份色图|想涩涩|多来点|来点色图|来张setu|来张色图|来点色色|色色|涩涩  (任意一个)
    
    张数: 1 2 3 4 ... 张|个|份  (可不填, 默认1)
    
    r18: 不填则不会出现r18图片, 填了会根据r18模式管理中的数据判断是否可返回r18图片
    
    关键词: 任意 (可不填)
    
    参考 (空格可去掉):   
    
        setu 10张 r18 白丝
        
        setu 10张 白丝
        
        setu r18 白丝
        
        setu 白丝
        
        setu

## 权限管理

注意：

1. 全部群聊或私聊默认均未在白名单, 但可以通过设置 setu_enable_private = True 将私聊默认全部开启, 群聊还需通过白名单管理指令添加。
2. superuser在任意聊天或在设置 setu_enable_private = True 的情况下好友私聊中, 会话均不受cd和白名单本身的影响, 但会受 撤回时长, r18, 最大张数 的影响。
3. 在群聊中默认以该群作为操作对象, 但在私聊需要用户提供操作对象。
4. 此部分的事件响应器均为 on_command 生成的, 触发时需要带有[命令头](https://v2.nonebot.dev/docs/api/config#Config-command_start)。

白名单管理：

    setu_wl add  添加会话至白名单
    setu_wl del  移出会话自白名单

r18模式管理：

    setu_r18 on  开启会话的r18模式
    setu_r18 off 关闭会话的r18模式

cd时间更新:

    setu_cd xxx  更新会话的冷却时间, xxx 为 int 类型的参数

撤回时间更新:

    setu_wd xxx  撤回前等待的时间, xxx 为 int 类型的参数

最大张数更新:

    setu_mn xxx  单次发送的最大图片数, xxx 为 int 类型的参数

## 其他指令

数据库更新:
>此指令默认从 github.com[^2] 拉取数据库，如果无法访问可以考虑使用科学上网或更换镜像。

    setu_db      从指定的路径拉取 lolicon.db 数据库，默认为此仓库
