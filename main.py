from sanic import Sanic
from sanic.response import json
import torch
import datetime
from transformers import AutoTokenizer, AutoModel
from peft import PeftModel




app = Sanic(__name__)
model = None
lora = None
async def load_model():
    global model,lora,tokenizer
    tokenizer = AutoTokenizer.from_pretrained("/root/model/chatglm2-6b", trust_remote_code=True, local_files_only=True)
    model = AutoModel.from_pretrained("/root/model/chatglm2-6b", trust_remote_code=True, local_files_only=True).half().cuda()
    #加载lora模型
    model = PeftModel.from_pretrained(model, "chatglm2-lora-dw",adapter_name='lora')
    

@app.listener('before_server_start')
async def before_start(app, loop):
    # 在服务器启动前异步加载语言模型
    loop.create_task(load_model())
    
@app.route('/p', methods=['POST'])
async def index(request):
    #关闭lora模型
    with model.disable_adapter(): 
        data = request.json
        prompt = data.get('prompt')
        history = data.get('history')
        # 记录当前时间
        response, history = model.chat(tokenizer,
                                    prompt,
                                    history=history)
    answer = {
        "response": response,
        "history": history,
        "status": 200,
        "time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    if torch.cuda.is_available():
            with torch.cuda.device(device=torch.device('cuda')):
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
    return json(answer,ensure_ascii=False)

@app.route('/l', methods=['POST'])
async def lora_web(request):
    data = request.json
    prompt = data.get('prompt')
    history = data.get('history')
    # 记录当前时间
    response, history = model.chat(tokenizer,
                                   prompt,
                                   history=history)
    answer = {
        "response": response,
        "history": history,
        "status": 200,
        "time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    if torch.cuda.is_available():
            with torch.cuda.device(device=torch.device('cuda')):
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
    return json(answer,ensure_ascii=False) 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True,single_process=True)
