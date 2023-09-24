FROM python:3.10.9-slim
WORKDIR /app
COPY . /app
RUN apt-get update  && apt install git wget -y && apt-get clean
RUN pip install -r requirements.txt
CMD python main.py