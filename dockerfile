FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime
WORKDIR /app
RUN apt-get update  && apt install git wget -y && apt-get clean 
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app
CMD ["python","main.py"]