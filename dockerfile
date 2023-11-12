FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

RUN apt-get update -y && apt-get install -y curl python3 python3-pip

RUN pip3 install fschat


