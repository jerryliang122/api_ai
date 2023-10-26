from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import os
import httpx
from model.chatglm import chatGLM2_6B
from concurrent.futures import ThreadPoolExecutor, wait
from qcloud_cos.cos_exception import CosClientError, CosServiceError
import fastcrc


class init_model:
    def __init__(self):
        secret_id = os.environ.get("SECRET_ID")
        secret_key = os.environ.get("SECRET_KEY")
        region = os.environ.get("REGION")
        self.bucket = os.environ.get("BUCKET")
        self.prefix = os.environ.get("PREFIX")
        token = None
        scheme = "http"
        config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
        self.client = CosS3Client(config)

    def file_list_url(self):
        urls = []
        response = self.client.list_objects(Bucket=self.bucket, Prefix=self.prefix)
        for file in response["Contents"]:
            url = self.client.get_presigned_url(Method="GET", Bucket=self.bucket, Key=file["Key"], Expired=300)
            print(f'读取文件{file["Key"]}', flush=True)
            if file["Key"] == self.prefix:
                continue
            urls.append((file["Key"], url))
        return urls

    def download_file(self, url, filename):
        retries = 0  # 设置重试次数的初始值
        max_retries = 5
        while retries < max_retries:
            try:
                with httpx.Client() as client:
                    r = client.get(url)
                    file = f"/tmp/{filename}"
                    with open(file, "wb") as f:
                        f.write(r.content)
                    server_crc = r.headers.get("x-cos-hash-crc64ecma")
                with open(file, "rb") as f:
                    local_crc = fastcrc.crc64.ecma_182(f)
                if server_crc == local_crc:
                    print(f"下载完成: {filename}", flush=True)
                else:
                    print(f"下载失败: {filename},校验错误，本地值:{str(local_crc)},服务器值:{str(server_crc)}", flush=True)
                return True
            except Exception as e:
                retries += 1
        print(f"无法下载文件: {filename}", flush=True)
        raise Exception("已达到最大重试次数")
        return False

    def main(self):
        urls = self.file_list_url()
        os.mkdir(f"/tmp/{self.prefix}")
        # 使用多线程的方式下载文件
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for file, url in urls:
                future = executor.submit(self.download_file, url, file)
                futures.append(future)
            wait(futures)
        return True
