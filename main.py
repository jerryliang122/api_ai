from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos.cos_exception import CosClientError
import sys
import os
import time

init_rate = 0


def percentage(consumed_bytes, total_bytes):
    """进度条回调函数，计算当前上传的百分比

    :param consumed_bytes: 已经上传/下载的数据量
    :param total_bytes: 总数据量
    """
    global init_rate
    if total_bytes:
        rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
        if rate > init_rate:
            print("正在上传" + str(rate) + "%\n", flush=True)
            sys.stdout.flush()
            current_time = time.time()  # 记录当前的时间
            elapsed_time = current_time - start_time  # 计算已经上传了多少时间
            speed = round(consumed_bytes / elapsed_time, 2)  # 计算每秒上传了多少字节
            print("每秒上传" + str(speed) + "bytes\n", flush=True)
            sys.stdout.flush()
            init_rate = rate


# 获取qcloud_secret_id环境变量
secret_id = os.environ.get("secret_id")
secret_key = os.environ.get("secret_key")
region = os.environ.get("region")
token = None  # 使用临时密钥需要传入 Token，默认为空，可不填
scheme = "https"  # 指定使用 http/https 协议来访问 COS，默认为 https，可不填
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
client = CosS3Client(config)
start_time = time.time()
print("开始上载", flush=True)
sys.stdout.flush()
try:
    response = client.upload_file(
        Bucket="jerryliang-10052152",
        LocalFilePath="chatglm2-6b-32K.zip",
        Key="chatglm2-6b-32K.zip",
        progress_callback=percentage,
        PartSize=1,
        MAXThread=10,
        EnableMD5=False,
    )
except CosClientError as e:
    response = client.upload_file(
        Bucket="jerryliang-10052152",
        LocalFilePath="chatglm2-6b-32K.zip",
        Key="chatglm2-6b-32K.zip",
        progress_callback=percentage,
        PartSize=1,
        MAXThread=10,
        EnableMD5=False,
    )
print(response["ETag"])
