from transformers import AutoTokenizer, AutoModel
import torch
import sys
sys.path.append("src")
from peft import PeftModel

DEVICE = "cuda"
DEVICE_ID = "0"
CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}" if DEVICE_ID else DEVICE

class chatGLM_6B():
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("/root/model/chatglm-6b", trust_remote_code=True, local_files_only=True)
        self.model = AutoModel.from_pretrained("/root/model/chatglm-6b", trust_remote_code=True, local_files_only=True).half().cuda()
        

    def __call__(self, prompt,history):
        response, history = self.model.chat(self.tokenizer,
                                   prompt,
                                   history=history,
                                   max_length=2048,
                                   top_p=0.7,
                                   temperature=0.95)
        #回收显存
        if torch.cuda.is_available():
            with torch.cuda.device(CUDA_DEVICE):
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
        return response, history
    def __del__(self):
        del self.model
        self.model = None
        self.tokenizer = None
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

class chatglm_lora():
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("/root/model/chatglm-6b", trust_remote_code=True, local_files_only=True)
        model = AutoModel.from_pretrained("/root/model/chatglm-6b", trust_remote_code=True, local_files_only=True).half().cuda()
        model = PeftModel.from_pretrained(model, "./chatglm-lora/")
        self.model = model.half().cuda()

    def __call__(self, prompt,history):
        response, history = self.model.chat(self.tokenizer,
                                   prompt,
                                   history=history)
        #回收显存
        if torch.cuda.is_available():
            with torch.cuda.device(CUDA_DEVICE):
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
        return response, history
    def __del__(self):
        del self.model
        self.model = None
        self.tokenizer = None
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()