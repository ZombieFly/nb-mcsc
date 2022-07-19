import asyncio
import socket
import re

from mcstatus import (
    JavaServer as js,
    BedrockServer as bs
    )

from .data import Server, Data
from .parser import Namespace


class UnknowServerType(ValueError):
    def __init__(self,ErrorInfo):
        super().__init__(self)
        self.error_info=f'未知的服务器类型"{ErrorInfo}"，该值应为"JE"与"BE"中的其中一个'
    def __str__(self):
        return self.error_info


def put_status(s_type: str, status: str):
    def put_be(status):
        return (
            re.sub(r"(§.)", "", (
                f"Title: {status.motd}-{status.map}\n"
                + f"Version: {status.version.brand}{status.version.version}\n"
                + f"Players: {status.players_online}/{status.players_max}\n"
                + f"Gamemode: {status.gamemode}"
                )
            )
        )

    def put_je(status):
        cut_title = (re.split(r'[\n]', status.description)[0]).strip()
        cut_dc = (''.join((re.split(r'[\n]', status.description))[1:])).strip()
        return (
            re.sub(r"(§.)", "", (
                (
                    (
                        f"Title: {cut_title}\n"
                        + f"Description: {cut_dc}\n"
                    )if '\n' in status.description else (
                        f'Tilte: {status.description}\n'
                        )
                )
                + f"Version: {status.version.name}\n"
                + f"Players: {status.players.online}/{status.players.max}"

                )

            )
        )
    return (
        put_be(status)
        if s_type == 'BE' else
        put_je(status)
    )


class Admin_Handle:

    @classmethod
    async def add(cls, args: Namespace) -> str:
        try:
            bs.lookup(args.address, 1.5).status()
            s_type = 'BE'
        except socket.gaierror:
            s_type = '域名解析失败，请检查输入是否正确'
        except socket.timeout:
            try:
                js.lookup(args.address).status()
                s_type = 'JE'
            except socket.timeout:
                s_type = '未找到处于开放状态的BE/JE服务器'
            except Exception as err:
                return f'发生出乎意料的错误\n{err}'
        except Exception as err:
            return f'发生出乎意料的错误\n{err}'

        if s_type in ['BE', 'JE']:
            Data().add_server(
                Server(name=args.name,
                       address=args.address,
                       s_type=s_type,
                       ex_open=False),
                args.user_id,
                args.group_id,
            )
            return (f"在目标主机发现{s_type}服务器\n"
                    + "添加服务器成功！"
                    )
        else:
            return s_type

    @classmethod
    async def rm(cls, args: Namespace) -> str:
        Data().remove_server(args.name, args.user_id, args.group_id)

        return "移除服务器成功！"

    @classmethod
    async def top(cls, args: Namespace) -> str:
        server_list = Data().get_server_list(args.user_id, args.group_id)
        if args.name in (
            server.name
            for server in server_list
                        ):
            obj = Data().top_server(args.name, args.user_id, args.group_id)

            return f"成功置顶{obj.name}({obj.address})"
        else:
            return "没有找到对应该名称的已记录服务器"

class Anyone_Handle():
    @classmethod
    async def list(cls, args: Namespace) -> str:
        server_list = Data().get_server_list(args.user_id, args.group_id)

        if server_list:
            result = "本群记录服务器列表如下：\n" + "\n".join(
                f"·[{server.s_type}]{server.name}({server.address})"
                for server in server_list
            )
        else:
            result = "本群服务器记录为空"

        return result

    @classmethod
    async def do_ping(cls, address, s_type):
        err_info = '获取状态失败'
        try:
            if s_type == 'JE':
                target = await js.async_lookup(address)
                status = await target.async_status()
            elif s_type == 'BE':
                target = bs.lookup(address)
                status = await target.async_status()
            else:
                raise UnknowServerType(s_type)
        except (asyncio.exceptions.TimeoutError, ConnectionRefusedError):
            #je超时 或 be连接被拒绝
            return err_info
        else:
            return put_status(s_type, status)

    @classmethod
    async def ping(cls, args: Namespace) -> str:
        try:
            server_list = Data().get_server_list(args.user_id, args.group_id)
            if args.name in (
                server.name
                for server in server_list
                            ):
                for server in server_list:
                    if args.name == server.name:
                        address = server.address
                        s_type = server.s_type
                        break
                result = await cls.do_ping(address, s_type)
                return result
            else:
                return "没有找到对应该名称的已记录服务器"
        except Exception as err:
            return f'发生出乎意料的错误\n{err}'

    @classmethod
    async def p(cls, args: Namespace) -> str:
        server_list = Data().get_server_list(args.user_id, args.group_id)
        if server_list:
            address = server_list[0].address
            s_type = server_list[0].s_type
            try:
                status = (
                    js.lookup(address).status()
                    if s_type == 'JE' else
                    bs.lookup(address, 3).status()
                    )
            except socket.timeout:
                status = False
            except Exception as err:
                return f'发生出乎意料的错误\n{err}'
            return (
                put_status(s_type, status)
                if status else "获取状态失败"
                )

        else:
            return "本群服务器记录为空"
