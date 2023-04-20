from sanic import Blueprint
from sanic.response import json
from transformers import AutoTokenizer, AutoModel
import torch
import datetime
import threading

origin_bp = Blueprint('origin', url_prefix='/origin')
#设置模型状态
model_stats_chatglm = False
model_loaded_chatglm = False

DEVICE = "cuda"
DEVICE_ID = "0"
CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}" if DEVICE_ID else DEVICE

#显存回收
def torch_gc():
    if torch.cuda.is_available():
        with torch.cuda.device(CUDA_DEVICE):
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
model_lock = threading.Lock()
#使用多线程加载模型
def load_model():
    global tokenizer, model, model_loaded_chatglm 
    model_lock.acquire()
    try:
        model_loaded_chatglm = True
        tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True)
        model = AutoModel.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True).half().cuda()
        #完成后将模型状态设置为True
    except Exception as e:
        #打印错误日志
        print(e)
        model_loaded_chatglm = False
        return
    global model_stats_chatglm
    model_stats_chatglm = True
    return
#当30分钟后没有访问，将模型状态设置为False，并回收模型
def reset_model_stats():
    global model_stats_chatglm,model_loaded_chatglm, model, tokenizer
    model_lock.acquire()
    #查看时间
    time_now = datetime.datetime.now()
    #如果当前时间与上次访问时间相差30分钟，回收模型
    if model_stats_chatglm == False:
        return
    if (time_now - time_visit).seconds > 1800:
        del model
        del tokenizer
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        model_stats_chatglm = False
        model_loaded_chatglm = False
    return

@origin_bp.route('/', methods=['POST'])
async def index(request):
    global time_visit
    data = request.json
    prompt = data.get('prompt')
    history = data.get('history')
    #获取标准时间
    time_visit = datetime.datetime.now()
    #如果模型未加载完成，返回错误信息
    if not model_stats_chatglm:
        if model_loaded_chatglm:
            return json({'response': '模型尚未准备就绪','history':[],"status": 500,"time":time_visit.strftime('%Y-%m-%d %H:%M:%S')})
        #使用多线程的方式加载模型
        threading.Thread(target=load_model).start()
        #设置定时器，每5秒执行一次
        threading.Timer(5, reset_model_stats).start()
        return json({'response': '模型尚未准备就绪','history':[],"status": 500,"time":time_visit.strftime('%Y-%m-%d %H:%M:%S')})
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
        "time": time_visit.strftime('%Y-%m-%d %H:%M:%S')
    }
    torch_gc()
    return json(answer,ensure_ascii=False)

