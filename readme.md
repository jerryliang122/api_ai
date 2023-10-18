# Docker容器启动脚本

## 概述

本文档介绍了在Docker容器内部启动的Shell脚本，该脚本主要用于配置环境变量和启动相关应用程序。脚本的主要功能是连接到腾讯云对象存储（Tencent Cloud Object Storage，COS）并运行一个名为 `main.py` 的Python应用程序。

## 使用方法

为了正确使用此Docker容器，需要按照以下步骤进行配置和启动：

1. **设置环境变量**:

   在Docker容器启动之前，确保设置以下环境变量：
   - `SECRET_ID`: 您的腾讯云COS API 密钥的ID。
   - `SECRET_KEY`: 您的腾讯云COS API 密钥的密钥。
   - `REGION`: 您的腾讯云COS存储桶所在的地区。
   - `BUCKET`: 您要连接的COS存储桶的名称。

   请确保这些环境变量正确设置，以便脚本能够访问腾讯云COS。

2. **运行脚本**:

   执行以下命令来运行Docker容器并启动脚本：

   ```bash
   docker run -e SECRET_ID=<Your_SECRET_ID> -e SECRET_KEY=<Your_SECRET_KEY> -e REGION=<Your_REGION> -e BUCKET=<Your_BUCKET> -it <your-docker-image>
