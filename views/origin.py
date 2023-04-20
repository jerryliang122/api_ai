from sanic import Blueprint
from sanic.response import json
import datetime
from transformers import AutoTokenizer, AutoModel 
import torch
import asyncio


origin_bp = Blueprint('origin', url_prefix='/origin')
#全局变量，用于存储模型和 tokenizer
tokenizer = None
model = None

# 全局变量，用于记录上次访问模型的时间
last_access_time = None

# 定义一个时间间隔，表示多长时间没有访问模型后自动关闭模型
TIMEOUT = 30 * 60  # 30 分钟

# 创建一个 asyncio.Event 对象
stop_event = asyncio.Event()

DEVICE = "cuda"
DEVICE_ID = "0"
CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}" if DEVICE_ID else DEVICE

#回收显存
def torch_gc():
    if torch.cuda.is_available():
        with torch.cuda.device(CUDA_DEVICE):
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

# 异步任务：加载模型
async def load_model():
    global tokenizer
    global model
    global last_access_time

    # 加载模型和 tokenizer
    tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True)
    model = AutoModel.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True).half().cuda()

    # 记录当前时间
    last_access_time = datetime.datetime.now()

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
            tokenizer = None
            last_access_time = None
            #回收显存
            torch_gc()
            break

        # 等待一段时间后再次检查
        await asyncio.sleep(60)  # 每分钟检查一次


@origin_bp.route('/', methods=['POST'])
async def index(request):
    global tokenizer
    global model
    global last_access_time

    data = request.json
    prompt = data.get('prompt')
    history = data.get('history')
    # 如果模型尚未加载，则创建异步任务来加载模型
    if tokenizer is None or model is None:
        task = asyncio.create_task(load_model())
        answer = {
            'response': '模型尚未准备就绪',
            'history': [],
            'status': 500,
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return json(answer,ensure_ascii=False)
    # 记录当前时间
    last_access_time = datetime.datetime.now()
    response, history = model.chat(tokenizer,
                                   prompt,
                                   history=history,
                                   max_length=2048,
                                   top_p=0.7,
                                   temperature=0.95)
    torch_gc()
    answer = {
        "response": response,
        "history": history,
        "status": 200,
        "time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    return json(answer,ensure_ascii=False)

