from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import os
import zipfile
import httpx


def download_file():
    # 获取qcloud_secret_id环境变量
    secret_id = os.environ.get("secret_id")
    secret_key = os.environ.get("secret_key")
    region = os.environ.get("region")
    token = None  # 使用临时密钥需要传入 Token，默认为空，可不填
    scheme = "https"  # 指定使用 http/https 协议来访问 COS，默认为 https，可不填
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
    client = CosS3Client(config)
    response = client.get_presigned_url(
        Bucket="jerryliang-10052152", Key="chatglm2-6b-32k.zip", Expired=120, Method="GET"
    )
    # 使用httpx 多线程下载
    with httpx.Client() as client:
        response = client.get(response)
        response.raise_for_status()
        # 保存到/tmp/chatglm2-6b-32K.zip
        with open("/tmp/chatglm2-6b-32K.zip", "wb") as f:
            f.write(response.content)
    # 解压/tmp/chatglm2-6b-32K.zip
    zip_file = zipfile.ZipFile("/tmp/chatglm2-6b-32K.zip")
    zip_extract = zip_file.extractall("/tmp/chatglm2-6b-32K")
    zip_extract.close()
    return True


if __name__ == "__main__":
    download_file()
