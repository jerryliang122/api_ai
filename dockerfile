FROM python:3.10.9-slim
WORKDIR /app
COPY . /app
RUN apt-get update  && apt install git git-lfs -y && apt-get clean
RUN cd /app && git clone https://huggingface.co/THUDM/chatglm2-6b-32k
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
CMD python main.py