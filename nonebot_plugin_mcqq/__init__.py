from nonebot import on_message, get_driver, on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageEvent, Message
from nonebot_plugin_guild_patch import GuildMessageEvent
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11.permission import GROUP_OWNER,GROUP_ADMIN


from .data_source import send_msg_to_mc, start_ws_server, stop_ws_server
from .utils import msg_rule,create_config_file,get_config,set_config
from typing import Union

import json

mc_qq = on_message(priority=5, rule=msg_rule, block=False)
restart_ws=on_command("mcqq 重启ws",aliases={"mcqq restart_ws"}, priority=7,permission=SUPERUSER)
set_mcqq_ip=on_command("mcqq 设置ip",aliases={"mcqq set_mcqq_ip"}, priority=7,permission=SUPERUSER)
set_mcqq_port=on_command("mcqq 设置端口",aliases={"mcqq set_mcqq_port"}, priority=7,permission=SUPERUSER)
set_mcqq_send_group_name=on_command("mcqq 设置是否发送群名",aliases={"mcqq set_mcqq_send_group_name"}, priority=7,permission=SUPERUSER)
set_mcqq_display_server_name=on_command("mcqq 设置是否显示服务器名",aliases={"mcqq set_mcqq_display_server_name"}, priority=7,permission=SUPERUSER)
add_mcqq_server=on_command("mcqq 添加服务器",aliases={"mcqq add_mcqq_server"}, priority=7,permission=SUPERUSER|GROUP_OWNER|GROUP_ADMIN)
remove_mcqq_server=on_command("mcqq 删除服务器",aliases={"mcqq remove_mcqq_server"}, priority=7,permission=SUPERUSER|GROUP_OWNER|GROUP_ADMIN)
driver = get_driver()

create_config_file()
# bot连接时
@driver.on_bot_connect
async def on_start():
    # 启动 WebSocket 服务器
    await start_ws_server()


@driver.on_bot_disconnect
async def on_close():
    # 关闭 WebSocket 服务器
    await stop_ws_server()


# 收到 群/频 道消息时
@mc_qq.handle()
async def handle_first_receive(bot: Bot, event: Union[GroupMessageEvent, GuildMessageEvent]):
    await send_msg_to_mc(bot=bot, event=event)

@restart_ws.handle()
async def _(bot: Bot, event: MessageEvent):
    try:
        await stop_ws_server()
    except:
        await restart_ws.send("ws停止失败")
    try:
        await start_ws_server()
    except:
        await restart_ws.send("ws启动失败")
    await restart_ws.finish("完成")
@set_mcqq_ip.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message=CommandArg()):
    arg = arg.extract_plain_text()
    config_json=get_config()
    config_json["mcqq_ws_ip"]=arg
    set_config(json.dumps(config_json,indent=4))
    await set_mcqq_ip.finish("完成，重启机器人生效")
@set_mcqq_port.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message=CommandArg()):
    arg = arg.extract_plain_text()
    config_json=get_config()
    config_json["mcqq_ws_port"]=int(arg)
    set_config(json.dumps(config_json,indent=4))
    await set_mcqq_port.finish("完成，重启机器人生效")
@set_mcqq_send_group_name.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message=CommandArg()):
    arg = arg.extract_plain_text()
    b=True
    if arg=="开" or "on" or "true":
        b=True
    elif arg=="关" or "off" or "false":
        b=False
    config_json=get_config()
    config_json["mcqq_send_group_name"]=b
    set_config(json.dumps(config_json,indent=4))
    await set_mcqq_send_group_name.finish("完成")
@set_mcqq_display_server_name.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message=CommandArg()):
    arg = arg.extract_plain_text()
    b=True
    if arg=="开" or "on" or "true":
        b=True
    elif arg=="关" or "off" or "false":
        b=False
    config_json=get_config()
    config_json["mcqq_display_server_name"]=b
    set_config(json.dumps(config_json,indent=4))
    await set_mcqq_display_server_name.finish("完成")
@add_mcqq_server.handle()
async def _(bot: Bot,event:Union[GroupMessageEvent, GuildMessageEvent],arg:Message=CommandArg()):
    arg = arg.extract_plain_text()
    config_json=get_config()
    servers:list =config_json["mcqq_servers_list"]
    if isinstance(event, GroupMessageEvent):
        for per_server in servers:
            if arg == per_server["server_name"]:
                if event.group_id in per_server["group_list"]:
                    await add_mcqq_server.finish("服务器已存在")
                else:
                    group_id=event.group_id
                    grouplist:list=per_server["group_list"]
                    grouplist.append(group_id)
                    set_config(json.dumps(config_json,indent=4))
                    await set_mcqq_send_group_name.finish("完成")
        grouplist:list=[]
        group_id=event.group_id
        grouplist.append(group_id)
        server={'server_name':arg,'group_list':grouplist,'guild_list':[]}
        servers.append(server)
        set_config(json.dumps(config_json,indent=4))
        await set_mcqq_send_group_name.finish("完成")
    elif isinstance(event, GuildMessageEvent):
        for per_server in servers:
            if arg == per_server["server_name"]:
                if {"guild_id": event.guild_id, "channel_id": event.channel_id} in per_server["guild_list"]:
                    await add_mcqq_server.finish("服务器已存在")
                else:
                    guild_id=event.guild_id
                    channel_id=event.channel_id
                    guild={"guild_id": guild_id, "channel_id": channel_id}
                    guildlist:list=per_server["guild_list"]
                    guildlist.append(guild)
                    set_config(json.dumps(config_json,indent=4))
                    await set_mcqq_send_group_name.finish("完成")
        guildlist:list=[]
        guild_id=event.guild_id
        channel_id=event.channel_id
        guild={"guild_id": guild_id, "channel_id": channel_id}
        guildlist.append(guild)
        server={'server_name':arg,'group_list':grouplist,'guild_list':[]}
        servers.append(server)
        set_config(json.dumps(config_json,indent=4))
        await set_mcqq_send_group_name.finish("完成")
@remove_mcqq_server.handle()
async def _(bot: Bot,event:Union[GroupMessageEvent, GuildMessageEvent],arg:Message=CommandArg()):
    arg = arg.extract_plain_text()
    config_json=get_config()
    servers:list =config_json["mcqq_servers_list"]
    if isinstance(event, GroupMessageEvent):
        for per_server in servers:
            if per_server["server_name"]==arg:
                if event.group_id in per_server["group_list"]:
                    group_list:list=per_server["group_list"]
                    group_id=event.group_id
                    group_list.remove(group_id)
                    if len(group_list)==0:
                        servers.remove(per_server)
        set_config(json.dumps(config_json,indent=4))
        await set_mcqq_send_group_name.finish("完成")
    elif isinstance(event, GuildMessageEvent):
        for per_server in servers:
            if per_server["server_name"]==arg:
                if {"guild_id": event.guild_id, "channel_id": event.channel_id} in per_server["guild_list"]:
                    guild_list:list=per_server["group_list"]
                    guild_id=event.guild_id
                    channel_id=event.channel_id
                    guild={"guild_id": guild_id, "channel_id": channel_id}
                    guild_list.remove(guild)
        set_config(json.dumps(config_json,indent=4))
        await set_mcqq_send_group_name.finish("完成")