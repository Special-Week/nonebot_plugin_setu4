# nonebot_plugin_setu
内置数据库的setu插件, 另外尝试降低因为风控发不出图的概率(随机修改左上角一颗像素点)

安装方式:
pip安装
pip install nonebot_plugin_setu4


env配置项:

    setu_cd                  setu的cd, 默认20s, 类型int                例如: setu_cd = 30
    
    setu_ban                 禁用名单, 默认空, 类型string数组           例如: setu_ban = ["114514","1919810"]
    
    setu_withdraw_time       setu撤回时间, 默认100s, 类型int            例如: setu_withdraw_time = 30
    
    setu_max_num             setu一次性最大数量, 默认10, 类型int        例如: setu_max_num = 20
    
    setu_save                setu时候保存到本地, 默认False, 类型bool    例如: setu_save = True
    
以上配置项, 均可不写


setu_save保存的位置是插件目录下的resource/img保存后下一次调用碰到这个setu就不需要再下载

一般无需科学上网, 但是先确保一下自己的服务器能否正常访问pixiv.re

setu_save实际上你不管填了啥, 无论False还是True亦或别的, 他都会变成True, 想要False的话env就别写这个, 不鸟他








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



数据库记录: 49119张
