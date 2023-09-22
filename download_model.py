from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import os
import httpx
import asyncio
import aiofiles

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
        async with aiofiles.open(filename, "wb") as f:
            # 使用await f.write来异步写入文件
            await f.write(r.content)


async def main():
    # 获取list
    os.mkdir("/tmp/chatglm2-6b-32k")
    urls = file_list_url()
    # 使用asyncio进行异步下载
    download_tasks = []
    for filename, url in urls:
        filename = f"/tmp/{filename}"
        task = asyncio.create_task(download_file(url, filename))
        download_tasks.append(task)
    await asyncio.gather(*download_tasks)


if __name__ == "__main__":
    asyncio.run(main())
