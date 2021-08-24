from argparse import Namespace as ArgNamespace

from nonebot.rule import ArgumentParser

from .data import Data

class Namespace(ArgNamespace):
    user_id: int
    group_id: int
    name: str
    address: str


mc_parser = ArgumentParser("mcs")

subparsers = mc_parser.add_subparsers(dest="handle")

ping = subparsers.add_parser("ping", help="check server once")
ping.add_argument("name")

p = subparsers.add_parser("p", help="check the top server")

add = subparsers.add_parser("add", help="add server")
add.add_argument("name")
add.add_argument("address")

remove = subparsers.add_parser("remove", help="remove server")
remove.add_argument("name")

top =subparsers.add_parser("top", help="set a top server")
top.add_parser("name")

list = subparsers.add_parser("list", help="show server list")