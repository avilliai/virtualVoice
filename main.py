import asyncio
import os
import random
import signal
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

import httpx
import requests
from PIL import Image, ImageTk
import threading
import time
import yaml  # 导入yaml库
from yiriob.adapters import ReverseWebsocketAdapter
from yiriob.bot import Bot
from yiriob.event import EventBus
from yiriob.event.events import GroupMessageEvent

with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)
token=config["gptSovitsapikey"]
global adapter
exit_event = threading.Event()
#下面都是传家宝函数
def random_str(random_length=7, chars='AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789@$#_%'):
    """
    生成随机字符串作为验证码
    :param random_length: 字符串长度,默认为6
    :return: 随机字符串
    """
    string = ''

    length = len(chars) - 1
    # random = Random()
    # 设置循环每次取一个字符用来生成随机数
    for i in range(random_length):
        string += (chars[random.randint(0, length)])
    return string
def promptConvert(input_list):
    for item in input_list:
        new_parts = []
        for part in item.get('parts', []):
            if isinstance(part, dict):  # 如果part是字典，保持不变
                new_parts.append(part)
            else:  # 如果part不是字典，转换成{'text': part}
                new_parts.append({'text': part})
        item['parts'] = new_parts
    return input_list
async def geminiCFProxy(ak, messages, proxyUrl="https://fbsvilli.netlify.app",model="gemini-1.5-flash"):
    url = f"{proxyUrl}/v1beta/models/{model}:generateContent?key={ak}"
    #print(requests.get(url,verify=False))
    async with httpx.AsyncClient(timeout=100) as client:
        r = await client.post(url, json={"contents": messages, "safetySettings": [
            {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', "threshold": "BLOCK_None"},
            {'category': 'HARM_CATEGORY_HATE_SPEECH', "threshold": "BLOCK_None"},
            {'category': 'HARM_CATEGORY_HARASSMENT', "threshold": "BLOCK_None"},
            {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', "threshold": "BLOCK_None"}]})
        print(r)
        return r.json()['candidates'][0]["content"]["parts"][0]["text"]
async def gptVitsSpeakers():
    url = "https://infer.acgnai.top/infer/spks"
    async with httpx.AsyncClient(timeout=100) as client:
        r = await client.post(url, json={
            "type": "tts",
            "brand": "gpt-sovits",
            "name": "anime"
        })
    return r.json()["spklist"]

try:
    GPTSOVITS_SPEAKERS = asyncio.run(gptVitsSpeakers())
    #print(GPTSOVITS_SPEAKERS)
except:
    print("GPTSOVITS_SPEAKERS获取失败")
modelscopeSpeakers=["BT", "塔菲", "阿梓", "otto", "丁真", "星瞳", "东雪莲", "嘉然", "孙笑川", "亚托克斯", "文静", "鹿鸣",
"奶绿", "七海", "恬豆", "科比"]
outVitsSpeakers=[
        "丁真",
        "AD学姐",
        "赛马娘",
        "黑手",
        "蔡徐坤",
        "孙笑川",
        "邓紫棋",
        "东雪莲",
        "塔菲",
        "央视配音",
        "流萤",
        "郭德纲",
        "雷军",
        "周杰伦",
        "懒洋洋",
        "女大学生",
        "烧姐姐",
        "麦克阿瑟",
        "马老师",
        "孙悟空",
        "海绵宝宝",
        "光头强",
        "陈泽",
        "村民",
        "猪猪侠",
        "猪八戒",
        "薛之谦",
        "大司马",
        "刘华强",
        "特朗普",
        "满穗",
        "桑帛",
        "李云龙",
        "卢本伟",
        "pdd",
        "tvb",
        "王者语音播报",
        "爱莉希雅",
        "岳山",
        "妖刀姬",
        "少萝宝宝",
        "天海",
        "王者耀",
        "蜡笔小新",
        "琪",
        "茉莉",
        "蔚蓝档案桃井",
        "胡桃",
        "磊哥游戏",
        "洛天依",
        "派大星",
        "章鱼哥",
        "蔚蓝档案爱丽丝",
        "阿梓",
        "科比",
        "于谦老师",
        "嘉然",
        "乃琳",
        "向晚",
        "优优",
        "茶总",
        "小然",
        "泽北",
        "夯大力",
        "奶龙",
        "fufu大王","妤萌"]
async def gptSoVitsGenerator(text, speaker):
    try:
        if len(GPTSOVITS_SPEAKERS[speaker]) > 1:
            prompt = [{"content": "对下面的文本进行情感倾向分析，结果只能从下面的列表：{GPTSOVITS_SPEAKERS[speaker]} 中选取，直接输出结果，不要回复任何其他内容，下面是需要分析的文本:{text}", "role": "user"}]
            prompt = promptConvert(prompt)
            r = await geminiCFProxy("AIzaSyCGZ5DQtj5t_WSNRVKOsWmC2n2HbvLWkOg", prompt)
            r = r.rstrip()
            for i in GPTSOVITS_SPEAKERS[speaker]:
                if i in r:
                    inclination = i
                    break
                inclination = "中立"
        else:
            inclination = "中立"
    except:
        inclination = "中立"

    url = "https://infer.acgnai.top/infer/gen"
    async with httpx.AsyncClient(timeout=100) as client:
        r = await client.post(url, json={
            "access_token": token,
            "type": "tts",
            "brand": "gpt-sovits",
            "name": "anime",
            "method": "api",
            "prarm": {
                "speaker": speaker,
                "emotion": inclination,
                "text": text,
                "text_language": "多语种混合",
                "text_split_method": "按标点符号切",
                "fragment_interval": 0.3,
                "batch_size": 1,
                "batch_threshold": 0.75,
                "parallel_infer": True,
                "split_bucket": True,
                "top_k": 10,
                "top_p": 1.0,
                "temperature": 1.0,
                "speed_factor": 1.0
            }
        })
    print(r.json())
    r=requests.get(r.json()['audio'])
    p = "test.wav"
    with open(p, "wb") as f:
        f.write(r.content)
    return p
async def modelScopeTTS(text, speaker):
    if text == "" or text == " ":
        text = "哼哼"

    headers = {
        "Content-Type": "application/json",
        "Origin": "https://www.modelscope.cn",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
        "Cookie": "cna=j117HdPDmkoCAXjC3hh/4rjk; ajs_anonymous_id=5aa505b4-8510-47b5-a1e3-6ead158f3375; t=27c49d517b916cf11d961fa3769794dd; uuid_tt_dd=11_99759509594-1710000225471-034528; log_Id_click=16; log_Id_pv=12; log_Id_view=277; xlly_s=1; csrf_session=MTcxMzgzODI5OHxEdi1CQkFFQ180SUFBUkFCRUFBQU12LUNBQUVHYzNSeWFXNW5EQW9BQ0dOemNtWlRZV3gwQm5OMGNtbHVad3dTQUJCNFkwRTFkbXAwV0VVME0wOUliakZwfHNEIp5sKWkjeJWKw1IphSS3e4R_7GyEFoKKuDQuivUs; csrf_token=TkLyvVj3to4G5Mn_chtw3OI8rRA%3D; _samesite_flag_=true; cookie2=11ccab40999fa9943d4003d08b6167a0; _tb_token_=555ee71fdee17; _gid=GA1.2.1037864555.1713838369; h_uid=2215351576043; _xsrf=2|f9186bd2|74ae7c9a48110f4a37f600b090d68deb|1713840596; csg=242c1dff; m_session_id=769d7c25-d715-4e3f-80de-02b9dbfef325; _gat_gtag_UA_156449732_1=1; _ga_R1FN4KJKJH=GS1.1.1713838368.22.1.1713841094.0.0.0; _ga=GA1.1.884310199.1697973032; tfstk=fE4KxBD09OXHPxSuRWsgUB8pSH5GXivUTzyBrU0oKGwtCSJHK7N3ebe0Ce4n-4Y8X8wideDotbQ8C7kBE3queYwEQ6OotW08WzexZUVIaNlgVbmIN7MQBYNmR0rnEvD-y7yAstbcoWPEz26cnZfu0a_qzY_oPpRUGhg5ntbgh_D3W4ZudTQmX5MZwX9IN8ts1AlkAYwSdc9sMjuSF8g56fGrgX9SFbgs5bGWtBHkOYL8Srdy07KF-tW4Wf6rhWQBrfUt9DHbOyLWPBhKvxNIBtEfyXi_a0UyaUn8OoyrGJ9CeYzT1yZbhOxndoh8iuFCRFg38WZjVr6yVWunpVaQDQT762H3ezewpOHb85aq5cbfM5aaKWzTZQ_Ss-D_TygRlsuKRvgt_zXwRYE_VymEzp6-UPF_RuIrsr4vHFpmHbxC61Ky4DGguGhnEBxD7Zhtn1xM43oi_fHc61Ky4DGZ6xfGo3-rjf5..; isg=BKKjOsZlMNqsZy8UH4-lXjE_8ygE86YNIkwdKew665XKv0I51IGvHCUz7_tDrx6l"

    }
    if speaker == "阿梓":
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Azusa-Bert-VITS2-2.3/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Azusa-Bert-VITS2-2.3/gradio/file="
    elif speaker == "BT":
        speaker = "Speaker"
        url = "https://www.modelscope.cn/api/v1/studio/MiDd1Eye/BT7274-Bert-VITS2/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/MiDd1Eye/BT7274-Bert-VITS2/gradio/file="
    elif speaker == "otto":
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/otto-Bert-VITS2-2.3/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/otto-Bert-VITS2-2.3/gradio/file="
    elif speaker == "塔菲":
        speaker = "taffy"
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Taffy-Bert-VITS2/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Taffy-Bert-VITS2/gradio/file="
    elif speaker == "星瞳":
        speaker = "XingTong"
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/XingTong-Bert-VITS2/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/XingTong-Bert-VITS2/gradio/file="
    elif speaker == "丁真":
        url = "https://s5k.cn/api/v1/studio/MiDd1Eye/DZ-Bert-VITS2/gradio/run/predict"
        newurp = "https://s5k.cn/api/v1/studio/MiDd1Eye/DZ-Bert-VITS2/gradio/file="
        speaker = "Speaker"
    elif speaker == "东雪莲":
        speaker = "Azuma"
        url = "https://s5k.cn/api/v1/studio/Outcast/Azuma-Bert-VITS2/gradio/run/predict"
        newurp = "https://s5k.cn/api/v1/studio/Outcast/Azuma-Bert-VITS2/gradio/file="
    elif speaker == "嘉然":
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Diana-Bert-VITS2-2.3/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Diana-Bert-VITS2-2.3/gradio/file="
    elif speaker == "孙笑川":
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/SXC-Bert-VITS2/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/SXC-Bert-VITS2/gradio/file="
    elif speaker == "鹿鸣":
        speaker = "Lumi"
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Lumi-Bert-VITS2/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Lumi-Bert-VITS2/gradio/file="
    elif speaker == "文静":
        speaker = "Wenjing"
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Wenjing-Bert-VITS2/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Wenjing-Bert-VITS2/gradio/file="
    elif speaker == "亚托克斯":
        speaker = "Aatrox"
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Aatrox-Bert-VITS2/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Aatrox-Bert-VITS2/gradio/file="
    elif speaker == "奶绿":
        speaker = "明前奶绿"
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/LAPLACE-Bert-VITS2-2.3/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/LAPLACE-Bert-VITS2-2.3/gradio/file="
    elif speaker == "七海":
        speaker = "Nana7mi"
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Nana7mi-Bert-VITS2/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Nana7mi-Bert-VITS2/gradio/file="
    elif speaker == "恬豆":
        speaker = "Bekki"
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Bekki-Bert-VITS2/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Bekki-Bert-VITS2/gradio/file="
    elif speaker == "科比":
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Kobe-Bert-VITS2-2.3/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Kobe-Bert-VITS2-2.3/gradio/file="
    elif speaker == "胡桃":
        speaker = "hutao"
        url = "https://www.modelscope.cn/api/v1/studio/Xzkong/AI-hutao/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/Xzkong/AI-hutao/gradio/file="
    data = {
        "data": [text, speaker, 0.5, 0.5, 0.9, 1, "auto", None, "Happy", "Text prompt", "", 0.7],
        "event_data": None,
        "fn_index": 0,
        "dataType": ["textbox", "dropdown", "slider", "slider", "slider", "slider", "dropdown", "audio", "textbox",
                     "radio", "textbox", "slider"],
        "session_hash": random_str(11, "abcdefghijklmnopqrstuvwxyz1234567890")
    }
    p = 'test.wav'
    async with httpx.AsyncClient(timeout=200, headers=headers) as client:
        r = await client.post(url, json=data)
        newurl = newurp + \
                 r.json().get("data")[1].get("name")
    async with httpx.AsyncClient(timeout=200, headers=headers) as client:
        r = await client.get(newurl)
        with open(p, "wb") as f:
            f.write(r.content)
        return p
async def outVits(text,speaker):
    # os.system("where python")
    #p = random_str() + ".mp3"
    #p = "data/voices/" + p
    p = "test.wav"
    url = f"https://api.lolimi.cn/API/yyhc/api.php?msg={text}&sp={speaker}"
    async with httpx.AsyncClient(timeout=200) as client:
        r = await client.get(url)
        print(r)
        newUrl = r.json().get("mp3")
        print("outvits语音合成路径：" + p)
        r1 = requests.get(newUrl)
        with open(p, "wb") as f:
            f.write(r1.content)
        return p

background_photo = None

# 读取配置文件
def load_config():
    with open("config.yaml", "r", encoding='utf-8') as file:
        return yaml.safe_load(file)

# 保存配置文件
def save_config(data):
    with open("config.yaml", "w", encoding='utf-8') as file:
        yaml.dump(data, file, allow_unicode=True)

def run_gui():
    global background_photo

    root = tk.Tk()
    root.title("virtual voice")

    def terminate_all():
        print("正在彻底终止所有任务...")

        try:
            if adapter:
                adapter.stop()
                print("适配器已停止")
        except Exception as e:
            print(f"停止适配器时出错: {e}")

        exit_event.set()

        if root:
            root.quit()
            print("Tkinter 事件循环已停止")

        try:
            os._exit(0)
        except Exception as e:
            print(f"强制退出时出错: {e}")

        # 5. 如果仍有残留，发送中断信号
        signal.raise_signal(signal.SIGTERM)
    def on_closing():
        global adapter,gui_thread
        terminate_all()

        root.destroy()
        sys.exit(0)
    root.protocol("WM_DELETE_WINDOW", on_closing)

    background_image = Image.open("bg.png")
    window_width = background_image.width // 5
    window_height = background_image.height // 5
    root.geometry(f"{window_width}x{window_height}+0+0")

    background_image = background_image.resize((window_width, window_height), Image.LANCZOS)
    background_photo = ImageTk.PhotoImage(background_image)

    background_label = tk.Label(root, image=background_photo)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    create_main_interface(root)

    root.mainloop()

def create_main_interface(root):
    global adapter
    for widget in root.winfo_children():
        widget.destroy()


    background_label = tk.Label(root, image=background_photo)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)


    tk.Label(root, text="说话人:", bg='white').grid(row=0, column=0, padx=10, pady=10)
    if list(GPTSOVITS_SPEAKERS)!=None:
        merged_list = modelscopeSpeakers+outVitsSpeakers+list(GPTSOVITS_SPEAKERS)
    else:
        merged_list = modelscopeSpeakers+outVitsSpeakers
    speakers = merged_list
    speaker_combobox = ttk.Combobox(root, values=speakers)
    speaker_combobox.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(root, text="文本", bg='white').grid(row=1, column=0, padx=10, pady=10)
    text_entry = tk.Entry(root)
    text_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(root, text="目标用户ID:", bg='white').grid(row=2, column=0, padx=10, pady=10)
    user_id_entry = tk.Entry(root)
    user_id_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(root, text="目标群ID:", bg='white').grid(row=3, column=0, padx=10, pady=10)
    group_id_entry = tk.Entry(root)
    group_id_entry.grid(row=3, column=1, padx=10, pady=10)

    github_link = tk.Label(root, text="源代码", fg="blue", cursor="hand2")
    github_link.grid(row=6, columnspan=2, pady=10)
    github_link.bind("<Button-1>", lambda e: os.startfile("https://github.com/avilliai/virtualVoice"))

    open_source_statement = tk.Label(root, text="本项目开源，欢迎贡献与交流！", bg='white')
    open_source_statement.grid(row=7, columnspan=2, pady=5)

    def send_message():
        def run_async():
            speaker = speaker_combobox.get()
            user_id = user_id_entry.get()
            group_id = group_id_entry.get()
            text= text_entry.get()
            print(f"说话人: {speaker}, 目标用户ID: {user_id}, 目标群ID: {group_id}, 文本: {text}")

            if speaker in modelscopeSpeakers:
                r=asyncio.run(modelScopeTTS(text,speaker))
            elif speaker in outVitsSpeakers:
                r=asyncio.run(outVits(text,speaker))
            elif speaker in GPTSOVITS_SPEAKERS:
                r=asyncio.run(gptSoVitsGenerator(text,speaker))
            image_path = Path(f"{os.getcwd()}/{r}")
            file_url = image_path.as_uri()
            print(group_id)
            if group_id!="":
                asyncio.run(adapter.send_custom_message({"action": "send_group_msg", "params": {"group_id": int(group_id), "message": [
                    {"type": "record",
                     "data": {"file": file_url, "url": "", "cache": True, "proxy": True,
                              "timeout": 30}}], "auto_escape": True}, "echo": "7f04cc0e047f6f9ed13fe495ecb468de"}
                                              ))  # 根据需要修改消息内容
            if user_id!="":
                asyncio.run(adapter.send_custom_message({"action": "send_private_msg", "params": {"user_id": int(user_id), "message": [{"type": "record", "data": {"file": file_url, "url": "", "cache": True, "proxy": True, "timeout": 30}}], "auto_escape": True}, "echo": "5d38ab27e825ad9b1acbfa07952f29b3"}))
        threading.Thread(target=run_async).start()
    send_button = tk.Button(root, text="发送", command=send_message)
    send_button.grid(row=4, columnspan=2, pady=20)


    config_button = tk.Button(root, text="初次使用请配置", command=lambda: show_config_page(root))
    config_button.grid(row=5, columnspan=2, pady=10)

def show_config_page(root):
    # 清空当前界面
    for widget in root.winfo_children():
        widget.destroy()


    background_label = tk.Label(root, image=background_photo)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    config_data = load_config()
    tk.Label(root, text="配置页面", bg='white', font=('Arial', 16)).pack(pady=10)

    entries = {}
    for key, value in config_data.items():
        tk.Label(root, text=key, bg='white').pack(pady=5)
        entry = tk.Entry(root)
        entry.insert(0, str(value))
        entry.pack(pady=5)
        entries[key] = entry


        if key == "gptSovitsapikey":
            github_link = tk.Label(root, text="申请apikey", fg="blue", cursor="hand2")
            github_link.pack(pady=5)
            github_link.bind("<Button-1>", lambda e: os.startfile("https://getkey.acgnai.top/"))  # 替换为你的仓库链接

    def save_config_data():
        data_to_save = {key: entry.get() for key, entry in entries.items()}
        save_config(data_to_save)
        print("配置已保存:", data_to_save)

    save_button = tk.Button(root, text="保存配置", command=save_config_data)
    save_button.pack(pady=20)


    back_button = tk.Button(root, text="返回主界面", command=lambda: create_main_interface(root))
    back_button.pack(pady=10)

async def backMission():

    bus = EventBus()
    global adapter

    adapter = ReverseWebsocketAdapter(host='127.0.0.1', port=3003, access_token='f', bus=bus)


    adapter.start()

    await asyncio.sleep(10)

    '''await adapter.send_custom_message({"action": "send_group_msg", "params": {"group_id": 879886836, "message": [
        {"type": "record",
         "data": {"file": "file:///D:/python/virtualVoice/test.wav", "url": "", "cache": True, "proxy": True,
                  "timeout": 30}}], "auto_escape": True}, "echo": "7f04cc0e047f6f9ed13fe495ecb468de"}
                                      )  # 根据需要修改消息内容'''

    await asyncio.Event().wait()


gui_thread = threading.Thread(target=run_gui)
gui_thread.start()


asyncio.run(backMission())




