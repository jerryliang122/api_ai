import os
import asyncio
import concurrent.futures
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos.cos_exception import CosClientError
import time
import sys
import math


start_time = time.time()
init_rate = 0
secret_id = os.environ.get("secret_id")
secret_key = os.environ.get("secret_key")
region = os.environ.get("region")
token = None
scheme = "https"
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)


def percentage(consumed_bytes, total_bytes):
    global init_rate
    if total_bytes:
        rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
        if rate > init_rate:
            sys.stdout.flush()
            current_time = time.time()
            elapsed_time = current_time - start_time
            speed = round(consumed_bytes / elapsed_time, 2)
            speed = round(speed / 1024 / 1024, 2)
            print(f"正在上传：{file} // 已完成:{rate} %  速度：{speed}MB", flush=True)
            sys.stdout.flush()
            init_rate = rate


async def upload_file(file, file_path_cos, PartSize):
    loop = asyncio.get_running_loop()
    try:
        client = CosS3Client(config)
        await loop.run_in_executor(
            None,
            client.upload_file(
                Bucket="ai-1251947439",
                Key=f"chatglm2-6b-32k/{file}",
                LocalFilePath=file_path_cos,
                PartSize=PartSize,
                progress_callback=percentage,
            ),
        )
    except Exception as e:
        print(f"上传文件 {file} 失败：{str(e)}")


def main():
    file_path = os.path.join(os.getcwd(), "chatglm2-6b-32k")
    file_names = os.listdir(file_path)
    global file
    for file in file_names:
        # 获取file的文件大小
        size = os.path.getsize(os.path.join(file_path, file))
        # 转换成MB
        size = round(size / 1024 / 1024, 2)
        # 将文件分块成9999
        PartSize = int(math.ceil(size / 9999))
        print(f"文件名:{file}  分块大小:{str(PartSize)}", flush=True)
        file_path_cos = os.path.join(file_path, file, PartSize)
        upload_file(file, file_path_cos)


if __name__ == "__main__":
    main()
    sys.stdout.flush()
