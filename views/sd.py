from sanic import Blueprint
from sanic.response import json 
import datetime
from transformers import AutoTokenizer, AutoModel
import torch
import asyncio
from model.stable_diffusion import drawing
import io


origin_bp = Blueprint('origin', url_prefix='/origin')

# 全局变量，用于记录上次访问模型的时间
last_access_time = None
loading = False
# 定义一个时间间隔，表示多长时间没有访问模型后自动关闭模型
TIMEOUT = 5 * 60  # 5 分钟

# 创建一个 asyncio.Event 对象
stop_event = asyncio.Event()

#定时器
async def timer():
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
            break
        #每隔一段时间检查一次
        await asyncio.sleep(5)



@origin_bp.route('/', methods=['POST'])
async def index(request):
    global last_access_time
    #加载模型
    global model
    if model is None:
        model = drawing()
    #启动定时器
    asyncio.create_task(timer())
    data = request.json
    prompt = data.get('prompt')
    # 记录当前时间
    last_access_time = datetime.datetime.now()
    response = model(prompt)
    # 返回二进制
    return json({"image": response})