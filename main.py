import time
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sse_starlette.sse import ServerSentEvent, EventSourceResponse
import datetime
import asyncio
from config import (
    ModelCard,
    ChatMessage,
    ModelList,
    ChatCompletionRequest,
    ChatCompletionResponseChoice,
    DeltaMessage,
    ChatCompletionResponseStreamChoice,
    ChatCompletionResponse,
    ChatRequest,
    ChatResponse,
)
import torch
import gc
from download_model import main


TIMEOUT = 120
model_lists = ["chatglm2-6b"]
model = None


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
    # 如果model是None挂起这个连接。直到加载完毕
    while model is None:
        model = await main()
    query = request.messages[-1].content
    last_access_time = datetime.datetime.now()
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
        generate = model.stream_chat(query, history, model_id=request.model, temperature=request.temperature)
        last_access_time = datetime.datetime.now()
        return EventSourceResponse(generate, media_type="text/event-stream")

    response, _ = model.chat(query, history=history, temperature=request.temperature)
    choice_data = ChatCompletionResponseChoice(
        index=0, message=ChatMessage(role="assistant", content=response), finish_reason="stop"
    )
    return ChatCompletionResponse(model=request.model, choices=[choice_data], object="chat.completion")


@app.post("/chatglm", response_model=ChatResponse)
async def create_chat_completion(request: ChatRequest):
    global model, last_access_time
    while model is None:
        model = await main()
    last_access_time = datetime.datetime.now()
    query = request.prompt
    history = request.history
    response, history = model.chat(query, history=history, temperature=request.temperature)
    return ChatResponse(response=response, status=200, history=history)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000, workers=1)
