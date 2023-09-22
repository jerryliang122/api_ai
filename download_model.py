from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import os
import httpx
import asyncio

# 初始化COS
secret_id = os.environ.get("secret_id")
secret_key = os.environ.get("secret_key")
region = os.environ.get("region")
token = None
scheme = "https"
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
client = CosS3Client(config)


# file_list
def file_list_url():
    urls = []
    response = client.list_objects(Bucket="ai-1251947439", Prefix="chatglm2-6b-32k/")
    for file in response["Contents"]:
        url = client.get_presigned_url(Method="GET", Bucket="ai-1251947439", Key=file["Key"], Expired=120)
        urls.append((file["Key"], url))
    return urls


# 使用httpx下载
async def download_file(url, filename):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        with open(filename, "wb") as f:
            f.write(r.content)
    return True


async def main():
    # 获取list
    urls = await file_list_url()
    print(urls)


if __name__ == "__main__":
    from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import os
import httpx

# 初始化COS
secret_id = os.environ.get("secret_id")
secret_key = os.environ.get("secret_key")
region = os.environ.get("region")
token = None
scheme = "https"
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
client = CosS3Client(config)


# file_list
def file_list_url():
    urls = []
    response = client.list_objects(Bucket="ai-1251947439", Prefix="chatglm2-6b-32k/")
    for file in response["Contents"]:
        url = client.get_presigned_url(Method="GET", Bucket="ai-1251947439", Key=file["Key"], Expired=120)
        urls.append((file["Key"], url))
    return urls


# 使用httpx下载
async def download_file(url, filename):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        with open(filename, "wb") as f:
            f.write(r.content)


async def main():
    # 获取list
    urls = file_list_url()
    # 使用asyncio进行异步下载
    download_tasks = []
    for filename, url in urls:
        filename = f"/tmp/{filename}"
        task = asyncio.create_task(download_file(url, filename))
        download_tasks.append(task)
    await asyncio.gather(*download_tasks)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
