from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import os
import httpx
from model.chatglm import chatGLM2_6B
from concurrent.futures import ThreadPoolExecutor
from qcloud_cos.cos_exception import CosClientError, CosServiceError


class init_model:
    def __init__(self):
        secret_id = os.environ.get("SECRET_ID")
        secret_key = os.environ.get("SECRET_KEY")
        region = os.environ.get("REGION")
        self.bucket = os.environ.get("BUCKET")
        self.prefix = os.environ.get("PREFIX")
        token = None
        scheme = "https"
        config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
        self.client = CosS3Client(config)

    def file_list_url(self):
        urls = []
        response = self.client.list_objects(Bucket=self.bucket, Prefix=self.prefix)
        for file in response["Contents"]:
            # url = self.client.get_presigned_url(Method="GET", Bucket=self.bucket, Key=file["Key"], Expired=120)
            url = 1
            print(f'读取文件{file["Key"]}', flush=True)
            if file["Key"] == self.prefix:
                continue
            urls.append((file["Key"], url))
        return urls

    def download_file(self, url, filename):
        for i in range(0, 10):
            try:
                self.client.download_file(
                    Bucket=self.bucket,
                    Key=filename,
                    DestFilePath=f"/tmp/{filename}",
                    PartSize=500,
                    EnableCRC=False,
                    MAXThread=4,
                )
                print(f"下载文件{filename}成功", flush=True)
                break
            except CosClientError or CosServiceError as e:
                print(f"下载失败:{filename}", flush=True)
                print(e, flush=True)

    def main(self):
        urls = self.file_list_url()
        os.mkdir(f"/tmp/{self.prefix}")
        # 使用多线程的方式下载文件
        with ThreadPoolExecutor(max_workers=1) as executor:
            for file, url in urls:
                executor.submit(self.download_file, url, file)
        return True
