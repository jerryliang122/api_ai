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
            sys.stdout.flush()
            current_time = time.time()  # 记录当前的时间
            elapsed_time = current_time - start_time  # 计算已经上传了多少时间
            speed = round(consumed_bytes / elapsed_time, 2)  # 计算每秒上传了多少字节
            # 将speed转换为MB
            speed = round(speed / 1024 / 1024, 2)
            print(f"正在上传：{file} // 已完成:{rate} %  速度：{speed}MB", flush=True)
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
# 获取当前目录下的chatglm2-6b-32k 文件
file_path = os.path.join(os.getcwd(), "chatglm2-6b-32k")
# 获取file_path目录下的文件名
file_name = os.listdir(file_path)
# 上传所有文件到cos
for file in file_name:
    file_path_cos = os.path.join(file_path, file)
    start_time = time.time()  # 记录开始时间
    client.upload_file(
        Bucket="ai-1251947439",
        Key=f"chatglm2-6b-32k/{file}",
        FilePath=file_path_cos,
        PartSize=50,
        progress_callback=percentage,
    )

sys.stdout.flush()
