from diffusers import DiffusionPipeline
from PIL import Image
import io
import base64
import torch

class drawing():
    def __init__(self):
        self.pipe = DiffusionPipeline.from_pretrained("/root/model/stable-diffusion-2-1", trust_remote_code=True, local_files_only=True)
        self.pipe = self.pipe.to("cuda")
        
    def __call__(self, prompt):
        image = self.pipe(prompt).images[0]
        buf = io.BytesIO()
        image.save(buf, format='png')
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode()
        return img_data
    
    def __del__(self):
        del self.pipe
        self.pipe = None
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()