from sanic import Blueprint
from sanic.response import json
import datetime
from transformers import AutoTokenizer, AutoModel
import torch
import asyncio
from model.chatglm import chatglm_lora


chatglm_l = Blueprint('chatglm_l', url_prefix='/chatglm_l')

# 全局变量，用于记录上次访问模型的时间
last_access_time = None
loading = False
model = None
# 定义一个时间间隔，表示多长时间没有访问模型后自动关闭模型
TIMEOUT = 1 * 60  # 5 分钟

# 创建一个 asyncio.Event 对象
stop_event = asyncio.Event()

#定时器
async def timer():
    global model,loading
    model = chatglm_lora()
    loading = True
    # 进入循环，等待下一次访问
    while not stop_event.is_set():
        # 计算当前时间和上次访问时间的差值
        time_since_last_access = (datetime.datetime.now() - last_access_time).total_seconds()
        # 如果超过了指定的时间间隔，则关闭模型
        if time_since_last_access > TIMEOUT:
            # 释放 GPU 显存
            del model
            # 清空全局变量
            model = None
            loading = False
            break
        #每隔一段时间检查一次
        await asyncio.sleep(5)



@chatglm_l.route('/', methods=['POST'])
async def index(request):
    global last_access_time
    last_access_time = datetime.datetime.now()
    #加载模型
    if model is None:
        #启动定时器
        asyncio.create_task(timer())
    while not loading:
        await asyncio.sleep(1)
    data = request.json
    prompt = data.get('prompt')
    history = data.get('history')
    # 记录当前时间
    last_access_time = datetime.datetime.now()
    response, history = model(prompt,history)

    answer = {
        "response": response,
        "history": history,
        "status": 200,
        "time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    return json(answer,ensure_ascii=False)

