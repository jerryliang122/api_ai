import time
import uvicorn
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Literal, Optional, Union
from sse_starlette.sse import ServerSentEvent, EventSourceResponse
import datetime
import asyncio
from model.chatglm import chatGLM2_6B

TIMEOUT = 300
model_lists = ["chatglm2-6b", "chatglm2-6b-lora"]


class ModelCard(BaseModel):
    id: str
    object: str = "model"
    created: int = Field(default_factory=lambda: int(time.time()))
    owned_by: str = "owner"
    root: Optional[str] = None
    parent: Optional[str] = None
    permission: Optional[list] = None


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ModelList(BaseModel):
    object: str = "list"
    data: List[ModelCard] = []


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_length: Optional[int] = None
    stream: Optional[bool] = False


class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Literal["stop", "length"]


class DeltaMessage(BaseModel):
    role: Optional[Literal["user", "assistant", "system"]] = None
    content: Optional[str] = None


class ChatCompletionResponseStreamChoice(BaseModel):
    index: int
    delta: DeltaMessage
    finish_reason: Optional[Literal["stop", "length"]]


class ChatCompletionResponse(BaseModel):
    model: str
    object: Literal["chat.completion", "chat.completion.chunk"]
    choices: List[Union[ChatCompletionResponseChoice, ChatCompletionResponseStreamChoice]]
    created: Optional[int] = Field(default_factory=lambda: int(time.time()))


# 创建一个 asyncio.Event 对象
stop_event = asyncio.Event()


# 模型加载器
async def timer(model_name):
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
        pass
    elif request.model != loading:
        raise HTTPException(status_code=400, detail=f"Model not loaded,Waiting for release: {time_since_last_access}")
    query = request.messages[-1].content

    prev_messages = request.messages[:-1]
    if len(prev_messages) > 0 and prev_messages[0].role == "system":
        query = prev_messages.pop(0).content + query

    history = []
    if len(prev_messages) % 2 == 0:
        for i in range(0, len(prev_messages), 2):
            if prev_messages[i].role == "user" and prev_messages[i + 1].role == "assistant":
                history.append([prev_messages[i].content, prev_messages[i + 1].content])

    response, _ = model.chat(query, history=history, lora=lora)
    choice_data = ChatCompletionResponseChoice(
        index=0, message=ChatMessage(role="assistant", content=response), finish_reason="stop"
    )
    last_access_time = datetime.datetime.now()
    return ChatCompletionResponse(model=request.model, choices=[choice_data], object="chat.completion")


