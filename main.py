from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import os

init_rate = 0


def percentage(consumed_bytes, total_bytes):
    """进度条回调函数，计算当前上传的百分比

    :param consumed_bytes: 已经上传/下载的数据量
    :param total_bytes: 总数据量
    """
    if total_bytes:
        rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
        if rate != init_rate:
            print("正在上传{0}% ".format(rate))
            init_rate = rate
            sys.stdout.flush()


# 获取qcloud_secret_id环境变量
secret_id = os.environ.get("secret_id")
secret_key = os.environ.get("secret_key")
region = os.environ.get("region")
token = None  # 使用临时密钥需要传入 Token，默认为空，可不填
scheme = "https"  # 指定使用 http/https 协议来访问 COS，默认为 https，可不填
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
client = CosS3Client(config)

response = client.upload_file(
    Bucket="jerryliang-10052152",
    LocalFilePath="chatglm2-6b-32K.zip",
    Key="chatglm2-6b-32K.zip",
    progress_callback=percentage,
)
print(response["ETag"])
