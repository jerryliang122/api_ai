FROM python:3.10.9-slim
WORKDIR /app
COPY . /app
RUN apt-get update  && apt install git wget -y && apt-get clean &&\
    wget https://github.com/tencentyun/cosfs/releases/download/v1.0.21/cosfs_1.0.21-ubuntu20.04_amd64.deb &&\
    dpkg -i cosfs_1.0.21-ubuntu20.04_amd64.deb &&\
    ln -s /root/.cache /tmp
RUN pip install -r requirements.txt
CMD python main.py