FROM python:3.10.9-slim
WORKDIR /app
COPY . /app
RUN apt-get update  && apt install git git-lfs -y && apt-get clean
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
CMD python main.py