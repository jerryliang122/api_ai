from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from transformers.generation import GenerationConfig
import torch
from config import *

DEVICE = "cuda"
DEVICE_ID = "0"
CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}" if DEVICE_ID else DEVICE


class Qwen_7B:
    def __init__(self):
        quantization_config = BitsAndBytesConfig(load_in_8bit=True)
        self.tokenizer = AutoTokenizer.from_pretrained(
            "/root/model/Qwen-7B-Chat", trust_remote_code=True, local_files_only=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            "/root/model/Qwen-7B-Chat",
            device_map="auto",
            trust_remote_code=True,
            local_files_only=True,
            quantization_config=quantization_config,
        ).eval()
        self.model.generation_config = GenerationConfig.from_pretrained(
            "/root/model/Qwen-7B-Chat", trust_remote_code=True, local_files_only=True
        )

    def chat(self, prompt, history, lora, temperature):
        if lora:
            response, history = self.model.chat(self.tokenizer, prompt, history=history)
        else:
            response, history = self.model.chat(self.tokenizer, prompt, history=history)
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
            for new_response, _ in self.model.chat_stream(self.tokenizer, prompt, history):
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
            for new_response, _ in self.model.chat_stream(self.tokenizer, prompt, history):
                if len(new_response) == current_length:
                    continue

                new_text = new_response[current_length:]
                current_length = len(new_response)

                choice_data = ChatCompletionResponseStreamChoice(
                    index=0, delta=DeltaMessage(content=new_text), finish_reason=None
                )
                chunk = ChatCompletionResponse(model=model_id, choices=[choice_data], object="chat.completion.chunk")
                yield "{}".format(chunk.json(exclude_unset=True, ensure_ascii=False))

        choice_data = ChatCompletionResponseStreamChoice(index=0, delta=DeltaMessage(), finish_reason="stop")
        chunk = ChatCompletionResponse(model=model_id, choices=[choice_data], object="chat.completion.chunk")
        yield "{}".format(chunk.json(exclude_unset=True, ensure_ascii=False))
        yield "[DONE]"

    def __del__(self):
        del self.model
        self.model = None
        self.tokenizer = None
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
