from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import os
import httpx
from model.chatglm import chatGLM2_6B


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
            url = self.client.get_presigned_url(Method="GET", Bucket=self.bucket, Key=file["Key"], Expired=120)
            print(file["Key"], flush=True)
            urls.append((file["Key"], url))
        return urls

    def download_file(self, url, filename):
        try:
            with httpx.Client() as client:
                r = client.get(url)
                file = f"/tmp/{self.prefix}/{filename}"
                with open(file, "wb") as f:
                    f.write(r.content)
            print(f"下载完成: {filename}", flush=True)
            return True
        except Exception as e:
            print(f"下载失败: {filename}", flush=True)
            raise Exception("已终止下载")
            return False

    def main(self):
        urls = self.file_list_url()
        os.mkdir(f"/tmp/{self.prefix}")
        for filename, url in urls:
            download = self.download_file(url, filename)
        return chatGLM2_6B()
