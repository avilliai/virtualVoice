import asyncio

from yiriob.adapters import ReverseWebsocketAdapter
from yiriob.event import EventBus


async def main():
    # 创建 EventBus 实例
    bus = EventBus()

    # 初始化适配器
    adapter = ReverseWebsocketAdapter(host='127.0.0.1', port=3003, access_token='f', bus=bus)

    # 启动 WebSocket 服务器
    adapter.start()

    # 发送自定义消息


    # 等待一段时间后关闭服务器
    await asyncio.sleep(10)
    # 发送自定义消息
    await adapter.send_custom_message({"action": "send_group_msg", "params": {"group_id": 879886836, "message": [{"type": "record", "data": {"file": "file:///D:/python/virtualVoice/test.wav", "url": "", "cache": True, "proxy": True, "timeout": 30}}], "auto_escape": True}, "echo": "7f04cc0e047f6f9ed13fe495ecb468de"}
)  # 根据需要修改消息内容

    # 等待一段时间后关闭服务器
    await asyncio.Event().wait()


# 运行主程序
asyncio.run(main())