from transformers import AutoTokenizer, AutoModel
import torch
import sys
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
import time

sys.path.append("src")

DEVICE = "cuda"
DEVICE_ID = "0"
CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}" if DEVICE_ID else DEVICE


class chatGLM2_6B:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("/tmp/chatglm2-6b-32k", trust_remote_code=True)
        self.model = AutoModel.from_pretrained("/tmp/chatglm2-6b-32k", trust_remote_code=True).half().cuda()

    def chat(self, prompt, history, temperature):
        response, history = self.model.chat(
            self.tokenizer, prompt, history=history, max_length=32000, top_p=0.7, temperature=temperature
        )
        # 回收显存
        if torch.cuda.is_available():
            with torch.cuda.device(CUDA_DEVICE):
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
        return response, history

    async def stream_chat(self, prompt, history, lora, model_id, temperature):
        choice_data = ChatCompletionResponseStreamChoice(
            index=0, delta=DeltaMessage(role="assistant"), finish_reason=None
        )
        chunk = ChatCompletionResponse(model=model_id, choices=[choice_data], object="chat.completion.chunk")
        yield "{}".format(chunk.json(exclude_unset=True, ensure_ascii=False))

        current_length = 0
        if lora:
            for new_response, _ in self.model.stream_chat(self.tokenizer, prompt, history, temperature=temperature):
                if len(new_response) == current_length:
                    continue

                new_text = new_response[current_length:]
                current_length = len(new_response)

                choice_data = ChatCompletionResponseStreamChoice(
                    index=0, delta=DeltaMessage(content=new_text), finish_reason=None
                )
                chunk = ChatCompletionResponse(model=model_id, choices=[choice_data], object="chat.completion.chunk")
                yield "{}".format(chunk.json(exclude_unset=True, ensure_ascii=False))
        else:
            with self.model.disable_adapter():
                for new_response, _ in self.model.stream_chat(self.tokenizer, prompt, history, temperature=temperature):
                    if len(new_response) == current_length:
                        continue

                    new_text = new_response[current_length:]
                    current_length = len(new_response)

                    choice_data = ChatCompletionResponseStreamChoice(
                        index=0, delta=DeltaMessage(content=new_text), finish_reason=None
                    )
                    chunk = ChatCompletionResponse(
                        model=model_id, choices=[choice_data], object="chat.completion.chunk"
                    )
                    yield "{}".format(chunk.json(exclude_unset=True, ensure_ascii=False))

        choice_data = ChatCompletionResponseStreamChoice(index=0, delta=DeltaMessage(), finish_reason="stop")
        chunk = ChatCompletionResponse(model=model_id, choices=[choice_data], object="chat.completion.chunk")
        yield "{}".format(chunk.json(exclude_unset=True, ensure_ascii=False))
        yield "[DONE]"

    def __del__(self):
        import gc

        del self.model
        del self.tokenizer
        self.model = None
        self.tokenizer = None
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        gc.collect()
