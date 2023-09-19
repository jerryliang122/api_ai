#获取secret_id 环境变量
export secret_id=$(echo $SECRET_ID)
#获取secret_key 环境变量
export secret_key=$(echo $SECRET_KEY)
#获取region 环境变量
export region=$(echo $REGION)
#使用echo 写入 
echo "$region:$secret_id:$secret_key" > /etc/passwd-cosfs
chmod 640 /etc/passwd-cosfs
cosfs $region /tmp/chatglm2-6b-32K -ourl=http://cos.$region.myqcloud.com -odbglevel=info -oallow_other
python3 main.py
exit 0