FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime
WORKDIR /app
RUN apt-get update -y && apt-get install -y curl python3 python3-pip git
COPY ./requirements.txt requirements.txt
RUN pip3 install -r requirements.txt && \
    git clone https://github.com/lm-sys/FastChat.git && cd FastChat &&  \
    pip3 install --upgrade pip && pip3 install -e ".[model_worker,webui]" 

