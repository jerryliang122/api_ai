from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import os

# 获取qcloud_secret_id环境变量
secret_id = os.environ.get("secret_id")
secret_key = os.environ.get("secret_key")
region = os.environ.get("region")
token = None  # 使用临时密钥需要传入 Token，默认为空，可不填
scheme = "https"  # 指定使用 http/https 协议来访问 COS，默认为 https，可不填
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
client = CosS3Client(config)

response = client.upload_file(
    Bucket="jerryliang-10052152", LocalFilePath="chatglm2-6b-32K.zip", Key="chatglm2-6b-32K.zip"
)
print(response["ETag"])
