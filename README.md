# nonebot_plugin_setu4

内置数据库的setu插件, 另外尝试降低因为风控发不出图的概率(图像左右镜像翻转, 随机修改左上角一颗像素点)

不喜欢繁杂的权限控制这里推荐[青春版](https://github.com/Special-Week/youth-version-of-setu4), 简化了很多设置, 群聊私聊全开, 只有必要的权限控制, 相比完整版功能精简

github仓库内顺便加了个一次性下载数据库内所有图片的脚本, 有需要可以看一下, 文件夹download_image内, 请勿团体大规模爬取, 造成代理服务器不可用

### 目前数据库共70359条记录

安装方式:

    pip install nonebot_plugin_setu4
    
    nb plugin install nonebot-plugin-setu4
    
    有能力尽量从本仓库clone, 因为pypi不一定最新

## env 配置项

>以下配置项均可不填，插件会按照默认值读取

|config             |type            |default    |example                                  |usage                                   |
|-------------------|----------------|-----------|-----------------------------------------|----------------------------------------|
|setu_disable_wlist |bool            |False      |setu_disable_wlist  = True               |是否禁用白名单检查(极度不推荐禁用)(详见权限控制系统)|
|setu_enable_private|bool            |False      |setu_enable_private = True               |是否允许未在白名单的私聊会话使用(详见权限控制系统)  |
|setu_perm_cfg_path |str             |see example|setu_perm_cfg_path = './data/setu4'      |会话(群号或QQ号)启用、r18及其他独立配置项  |
|setu_save          |str             |None       |setu_save = './data/setu4/img'           |setu保存到本地的路径, 留空则不保存至本地   |
|setu_database_path |str             |see example|setu_database_path = see description[^1] |更新使用的数据库的地址, 默认为此项目的resource文件夹下|
|setu_cd*           |int             |20         |setu_cd = 30                             |setu默认cd[0,+∞], 为0时无cd              |
|setu_withdraw_time*|int             |100        |setu_withdraw_time = 30                  |setu默认撤回时间[0,100], 为0时不撤回      |
|setu_max_num*      |int             |10         |setu_max_num = 20                        |setu默认一次性最大数量[1,25]              |

>带有*标识的设置项可在指定群聊被setu_perm_cfg.json中的内容覆盖

[^1]:"https://raw.githubusercontent.com/Special-Week/nonebot_plugin_setu4/main/nonebot_plugin_setu4/resource/lolicon.db"

setu_save保存后下一次调用碰到这个setu会先从这个文件夹中进行匹配, 不需要再下载, 需要先要自己创建好文件夹

一般无需科学上网, 但希望你确认一下图片代理是否可用:   

    一些也许可用的pixiv代理: "i.pixiv.re" , "sex.nyan.xyz" , "px2.rainchan.win" , "pximg.moonchan.xyz" , "piv.deception.world" , "px3.rainchan.win" , "px.s.rainchan.win" , "pixiv.yuki.sh" , "pixiv.kagarise.workers.dev" , "pixiv.kagarise.workers.dev"

    使用插件提供的on_command响应器进行更换(on_command响应器注意.env内的命令头, 默认的代理为i.pixiv.re)  
    使用superuser账号发送: setu_proxy xxx      Example: setu_proxy i.pixiv.re
    警告: 这部分带了一个ping代理服务器的操作, 这个响应器是superuser only, 用了os.popen().read()操作, 请不要尝试给自己电脑注入指令
    
    Example: 
        数据库给的url为: https://i.pixiv.re/img-original/img/2022/07/09/18/51/03/99606781_p0.jpg

        有些代理可能会暂时不可用, 可以用来换成可用的代理, 比如px2.rainchan.win

        即: https://px2.rainchan.win/img-original/img/2022/07/09/18/51/03/99606781_p0.jpg

        能正常访问即可用

## 权限控制系统

本插件的权限控制系统分为两个部分：黑名单和白名单。此部分内容被存储在setu_perm_cfg_path中的setu_perm_cfg.json，其结构如下所示:

```python
{
    "group_114":{
        "cd"       : 30,     # cd时长
        "r18"      : True,   # r18开关
        "withdraw" : 100,    # 撤回延时
        "maxnum"   : 10      # 单次最高张数
    },
    "last":{                 # 最近一次发送setu的时间, 用于计算剩余的冷却时间, 此部分不会被积极写入文件, 仅更新内存
        "user_1919" : 810    
    },
    "ban":[                  # 黑名单, 禁用的群组或用户，跨会话生效, 会覆盖白名单设置
        "user_1919",         
        "group_810"
    ],
    "proxy": "i.pixiv.re"    # 代理, 用于替换数据库中的url
}
```

在插件运行中，权限控制系统会按照如下顺序进行检查：

1. 检查该会话是否在黑名单中存在，若存在则检查不通过。
2. 检查该会话是否屏蔽了白名单(即setu_disable_wlist = True)，若屏蔽则跳过第3~4步的检查(认为通过)。
3. 检查该会话是否为 `群聊类型` 或 `setu_enable_private = False 下的私聊类型`，若不是则跳过第4步的检查(认为通过)。
4. 检查该会话是否在白名单中存在，若不存在则检查不通过。
5. 检查该会话的冷却时间是否归零，若未归零则检查不通过。
6. 在以上检查通过的情况下，读取其他配置项并通过检查。

此部分的内容可以参考权限控制模块的[对应部分](./nonebot_plugin_setu4/permission_manager.py)进行理解。

## 获取setu

    命令头: setu|色图|涩图|想色色|来份色色|来份色图|想涩涩|多来点|来点色图|来张setu|来张色图|来点色色|色色|涩涩  (任意一个)
    
    张数: 1 2 3 4 ... 张|个|份  (可不填, 默认1)
    
    r18: 不填则不会出现r18图片, 填了会根据r18模式管理中的数据判断是否可返回r18图片
    
    关键词: 任意, 多tag使用空格分开 (可不填)
    
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

黑名单管理：

    setu_ban add  添加会话至黑名单
    setu_ban del  移出会话自黑名单

r18模式管理：

    setu_r18 on  开启会话的r18模式
    setu_r18 off 关闭会话的r18模式

cd时间更新:

    setu_cd xxx  更新会话的冷却时间, xxx 为 int 类型的参数

撤回时间更新:

    setu_wd xxx  撤回前等待的时间, xxx 为 int 类型的参数

最大张数更新:

    setu_mn xxx  单次发送的最大图片数, xxx 为 int 类型的参数

更换setu代理服务器:

    setu_proxy xxx   使用的代理服务器, xxx 为 string 类型的参数
    警告: 这部分带了一个ping代理服务器的操作, 这个响应器是superuser only, 用了os.popen().read()操作, 请不要尝试给自己电脑注入指令
    
​    

## 其他指令

获取插件帮助信息:

    "setu_help" | "setu_帮助" | "色图_help" | "色图_帮助"

查询黑白名单:

    "setu_roste" | "色图名单"


数据库更新(未完工):
>此指令默认从 github.com[^2] 拉取数据库，如果无法访问可以考虑使用科学上网或更换镜像或者手动从仓库下载换上去。

    setu_db      从指定的路径拉取 lolicon.db 数据库，默认为此仓库
