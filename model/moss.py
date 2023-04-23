from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

DEVICE = "cuda"
DEVICE_ID = "0"
CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}" if DEVICE_ID else DEVICE

class moss_model():
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("/root/model/moss-moon-003-sft-plugin-int4", trust_remote_code=True, local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained("/root/model/moss-moon-003-sft-plugin-int4", trust_remote_code=True).half().cuda()

    def __call__(self,prompt,history):
        plain_text = "<|Human|>:"+prompt+"<eoh>\n<|MOSS|>:"
        inputs = self.tokenizer(plain_text, return_tensors="pt")
        for k in inputs:
            inputs[k] = inputs[k].cuda()
        outputs = self.model.generate(**inputs, max_length=2048, do_sample=True, top_k=50, top_p=0.95, temperature=0.95, num_return_sequences=1)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        #构建History
        history = history + plain_text + response + "<eoh>\n"
        #回收显存
        if torch.cuda.is_available():
            with torch.cuda.device(CUDA_DEVICE):
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
        return response, history
    
    def __del__(self):
        del self.model
        del self.tokenizer
        self.model = None
        self.tokenizer = None
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
    