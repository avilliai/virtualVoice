import os
from pathlib import Path

import yaml
from yiriob.adapters import ReverseWebsocketAdapter
from yiriob.bot import Bot
from yiriob.event import EventBus
from yiriob.event.events import GroupMessageEvent
from yiriob.message import Record

with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)
bus = EventBus()
bot = Bot(
    adapter=ReverseWebsocketAdapter(
        host=config["ReverseWebsocketHost"], port=int(config["ReverseWebsocketPort"]),
        access_token=str(config["access_token"]), bus=bus
    ),
    self_id=int(config["qq_number"]),
)
@bus.on(GroupMessageEvent)
async def on_group_message(event: GroupMessageEvent) -> None:
    #发送本地语音
    image_path = Path(f"{os.getcwd()}/plugins/output.wav")
    file_url = image_path.as_uri()
    await bot.send_private_message(3552663628, [Record(file=file_url,url="")])
    #发送网络语音
    #await bot.send_group_message(event.group_id,[Record(file="https_url",url="")])'''
bot.run()