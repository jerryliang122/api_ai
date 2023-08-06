import time
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sse_starlette.sse import ServerSentEvent, EventSourceResponse
import datetime
import asyncio
from model.chatglm import chatGLM2_6B
from config import (
    ModelCard,
    ChatMessage,
    ModelList,
    ChatCompletionRequest,
    ChatCompletionResponseChoice,
    DeltaMessage,
    ChatCompletionResponseStreamChoice,
    ChatCompletionResponse,
)

TIMEOUT = 300
model_lists = ["chatglm2-6b", "chatglm2-6b-lora"]
loading = None
last_access_time = None

# 创建一个 asyncio.Event 对象
stop_event = asyncio.Event()


# 模型加载器
async def load_model(model_name):
    global model, loading, time_since_last_access, lora
    if model_name == model_lists[0]:
        model = chatGLM2_6B()
        loading = model_name
        lora = False
    elif model_name == model_lists[1]:
        model = chatGLM2_6B()
        loading = model_name
        lora = True

    # 进入循环，等待下一次访问
    while not stop_event.is_set():
        if last_access_time == None:
            break
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
        # 每隔一段时间检查一次
        await asyncio.sleep(5)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 设计V1版本的接口
@app.get("/v1/models", response_model=ModelList)
async def list_models():
    global model_args
    for model in model_lists:
        model_card = ModelCard(id=model)
    return ModelList(data=[model_card])


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest):
    global model, last_access_time

    if request.messages[-1].role != "user":
        raise HTTPException(status_code=400, detail="Invalid request")
    if loading == None:
        # 阻塞模式下加载模型
        await asyncio.create_task(load_model(request.model))
    elif request.model != loading:
        raise HTTPException(status_code=400, detail=f"Model not loaded,Waiting for release: {time_since_last_access}")
    query = request.messages[-1].content

    prev_messages = request.messages[:-1]
    if len(prev_messages) > 0 and prev_messages[0].role == "system":
        query1 = prev_messages.pop(0).content + query

    history = []
    if len(prev_messages) % 2 == 0:
        for i in range(0, len(prev_messages), 2):
            if prev_messages[i].role == "user" and prev_messages[i + 1].role == "assistant":
                history.append([prev_messages[i].content, prev_messages[i + 1].content])
    # 流式传输
    if request.stream:
        generate = model.stream_chat(query, history, lora=lora, model_id=request.model)
        last_access_time = datetime.datetime.now()
        return EventSourceResponse(generate, media_type="text/event-stream")

    response, _ = model.chat(query, history=history, lora=lora)
    choice_data = ChatCompletionResponseChoice(
        index=0, message=ChatMessage(role="assistant", content=response), finish_reason="stop"
    )
    last_access_time = datetime.datetime.now()
    return ChatCompletionResponse(model=request.model, choices=[choice_data], object="chat.completion")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)
