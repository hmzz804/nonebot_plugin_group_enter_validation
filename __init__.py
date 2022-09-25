import json
import os
import random
from argparse import Namespace

from nonebot import Config, get_driver
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import Event, PrivateMessageEvent
from nonebot.log import logger
from nonebot.params import ShellCommandArgs
from nonebot.permission import SUPERUSER
from nonebot.plugin import on_request, on_shell_command
from nonebot.rule import ArgumentParser

KEY_PATH = r"data/group_entry_key.json"
env_config = Config(**get_driver().config.dict())

try:
    key_length = env_config.group_login_key_length
except:
    logger.warning("配置项中未找到自定义的密钥长度，将采用默认值10")
    key_length = 10

if not os.path.exists("data"):
    os.mkdir("data")
if not os.path.exists(KEY_PATH):
    with open(KEY_PATH, "w") as g:
        initialize_dict = {}
        json.dump(initialize_dict, g, indent=4)

def read(path:str):
    with open(path, "r") as a:
        content = json.load(a)
    return content

def write_in(path:str,new_content) -> None :
    with open(path, 'w') as b:
        json.dump(new_content, b, indent=4)

def create_key(length:int, num:int) -> list:
    key_list = list(r"AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz1234567890-_=+*#")
    keys = []
    for j in range(num):
        key = ""
        for i in range(length):
            key += random.choice(key_list)
        keys.append(key)
    return keys

async def check_event(event: Event) -> bool:
    return event.post_type == "request" and event.request_type == "group" and event.sub_type == "add"

group_login = on_request(rule=check_event)
@group_login.handle()
async def group_handle(
    event:Event,
    bot:Bot
):
    event_json = json.loads(event.json())
    num = event_json['comment'].find("答案：")
    user_answer = event_json["comment"][num+3:]
    group_id = str(event_json['group_id'])
    groups_info = (read(path=KEY_PATH))

    if group_id in (groups_info.keys()):
        add_bool = False
        for i in groups_info[group_id]:
            if user_answer == i['key'] and i['state'] == 0:
                i['state'], i['user'] = 1, str(event_json['user_id'])
                await bot.set_group_add_request(
                    flag = event_json['flag'],
                    sub_type = event_json['sub_type']
                )
                add_bool = True
                break
        if not add_bool:
            await bot.set_group_add_request(
                flag = event_json['flag'],
                sub_type = event_json['sub_type'],
                approve = False,
                reason = "密钥错误或已被其他人使用！"
            )
        write_in(path=KEY_PATH, new_content=groups_info)
    else:
        logger.warning(f"收到加群（{event_json['group']}）请求，但未找到此群的密钥存储，已忽略本次请求")
        group_login.finish()

get_key_args_parser = ArgumentParser()
get_key_args_parser.add_argument('-n', '--num', type=int, default=1)
get_key_args_parser.add_argument('-g', '--group', type=int, default=None)

get_key = on_shell_command(
    cmd="创建加群密钥",
    parser=get_key_args_parser,
    permission=SUPERUSER
)
@get_key.handle()
async def get_key_handle(
    bot: Bot,
    event: PrivateMessageEvent,
    args: Namespace = ShellCommandArgs()
):
    if not args.group:
        await get_key.finish(message="群号呢")
    if not (args.num <= 30 and args.num >= 1):
        await get_key.finish(message="获取密钥个数最小为1个，最大为30个")
    groups_info = read(path=KEY_PATH)
    group_id, key_num, keys_list = str(args.group), int(args.num), create_key(length=key_length, num=args.num)
    if group_id not in (groups_info.keys()):
        await get_key.send(message=f"群{group_id}初次使用，正在新建此群存储的密钥")
        groups_info[group_id] = []
    for i in range(len(keys_list)):
        key_dict = {
            "key": keys_list[i],
            "state": 0,
            "creator": str(event.user_id),
            "user": ""
        }
        groups_info[group_id].append(key_dict)
    send_key = f'\n'.join(keys_list)
    write_in(path=KEY_PATH, new_content=groups_info)
    await get_key.finish(
        message=f"创建密钥成功！\n"
        +f"群“{group_id}”的{key_num}个加群密钥\n"
        +send_key
    )
    

