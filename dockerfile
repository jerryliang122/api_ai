FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

RUN apt-get update -y && apt-get install -y curl python3 python3-pip
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3 get-pip.py
RUN pip3 install plotly einops transformers_stream_generator

WORKDIR /data/fschat
ADD . .

RUN pip3 install -e ".[model_worker, webui]"
