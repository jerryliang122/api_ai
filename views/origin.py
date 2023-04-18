from sanic import Blueprint
from sanic.response import json
from transformers import AutoTokenizer, AutoModel
import torch
import datetime
import threading

origin_bp = Blueprint('origin', url_prefix='/origin')
DEVICE = "cuda"
DEVICE_ID = "0"
CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}" if DEVICE_ID else DEVICE


def torch_gc():
    if torch.cuda.is_available():
        with torch.cuda.device(CUDA_DEVICE):
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
model_stats = False
model_loaded = False
#使用多线程加载模型
def load_model():
    global tokenizer, model, model_loaded
    try:
        model_loaded = True
        tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True, local_files_only=True)
        model = AutoModel.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True, local_files_only=True).half().cuda()
        #完成后将模型状态设置为True
    except Exception as e:
        #打印错误日志
        print(e)
        model_loaded = False
        return
    global model_stats
    model_stats = True
    return

@origin_bp.route('/', methods=['POST'])
async def index(request):
    data = request.json
    prompt = data.get('prompt')
    history = data.get('history')
    #获取标准时间
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #如果模型未加载完成，返回错误信息
    if not model_stats:
        if model_loaded:
            return json({'response': '模型尚未准备就绪','history':[],"time":time})
        #使用多线程的方式加载模型
        threading.Thread(target=load_model).start()
        return json({'response': '模型尚未准备就绪','history':[],"time":time})
    #如果模型加载完成，返回结果
    response, history = model.chat(tokenizer,
                                   prompt,
                                   history=history,
                                   max_length=2048,
                                   top_p=0.7,
                                   temperature=0.95)
    answer = {
        "response": response,
        "history": history,
        "status": 200,
        "time": time
    }
    torch_gc()
    return json(answer,ensure_ascii=False)
