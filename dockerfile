FROM python:3.10.9-slim
WORKDIR /app
RUN apt-get update  && apt install git wget -y && apt-get clean 
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app
CMD ["python","main.py"]