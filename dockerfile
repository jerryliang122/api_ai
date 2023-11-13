FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

RUN apt-get update -y && apt-get install -y curl python3 python3-pip
COPY ./requirements.txt requirements.txt
RUN pip3 install fschat && \
    pip3 install -r requirements.txt


