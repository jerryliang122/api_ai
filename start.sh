#获取secret_id 环境变量
export secret_id=$(echo $SECRET_ID)
#获取secret_key 环境变量
export secret_key=$(echo $SECRET_KEY)
#获取region 环境变量
export region=$(echo $REGION)
#获取存储桶名称
export bucket=$(echo $BUCKET)
#使用echo 写入 
echo "$bucket:$secret_id:$secret_key" > /etc/passwd-cosfs
chmod 640 /etc/passwd-cosfs
cosfs $bucket /tmp -ourl=http://cos.$region.myqcloud.com -odbglevel=info -oallow_other
python3 main.py
exit 0