FROM python:3.10.9-slim
WORKDIR /app
COPY . /app
COPY /mnt/chatglm2-6b-32k /app/
RUN apt-get update  && apt install git -y && apt-get clean
RUN pip install -r requirements.txt
CMD python main.py