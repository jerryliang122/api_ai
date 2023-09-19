FROM python:3.10.9-slim
WORKDIR /app
COPY . /app
RUN echo "192.168.1.106 deb.debian.org" >> /etc/hosts && \
    apt-get update  && apt install git -y && apt-get clean &&\
    ln -s /root/.cache /tmp
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
CMD python main.py