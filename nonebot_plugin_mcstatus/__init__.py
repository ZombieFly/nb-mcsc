import nonebot
from nonebot.plugin import on_shell_command, require
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import (
    Bot,
    MessageEvent,
    PrivateMessageEvent,
    GroupMessageEvent,
)

from .parser import mc_parser
from .handle import Admin_Handle, Anyone_Handle
from .data import Data

# 注册 shell_like 事件响应器
mcs = on_shell_command("mcs", parser=mc_parser, priority=5)


@mcs.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    args = state["args"]
    args.user_id = event.user_id if isinstance(event, PrivateMessageEvent) else None
    args.group_id = event.group_id if isinstance(event, GroupMessageEvent) else None
    args.is_admin = (
        event.sender.role in ["admin", "owner"]
        if isinstance(event, GroupMessageEvent)
        else False
    )
    if hasattr(args, "handle"):
        try:
            #优先尝试执行Anyone权限命令
            result = await getattr(Anyone_Handle, args.handle)(args)
            if result:
                await bot.send(event, result)
        except:
            if args.is_admin:
                #尝试执行Admin权限命令
                try:
                    result = await getattr(Admin_Handle, args.handle)(args)
                    if result:
                        await bot.send(event, result)
                except AttributeError:
                    await bot.send(event, "未知命令")
                
