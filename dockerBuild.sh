#!/bin/bash

# 定义镜像名称和版本号
IMAGE_NAME="jsonstiananan/pretender-proxy"
VERSION="v$(date '+%Y%m%d%H%M%S')"

echo "构建镜像: $IMAGE_NAME:$VERSION"
docker build -t $IMAGE_NAME:$VERSION .

# 添加 latest 标签（会覆盖之前的latest）
docker tag $IMAGE_NAME:$VERSION $IMAGE_NAME:latest

echo "镜像构建完成:"
echo "  - $IMAGE_NAME:$VERSION"
echo "  - $IMAGE_NAME:latest (覆盖之前的latest标签)"

# 推送镜像
echo "推送镜像到Docker Hub..."
echo "推送版本标签: $IMAGE_NAME:$VERSION"
docker push $IMAGE_NAME:$VERSION

echo "推送latest标签 (将替换Docker Hub上的旧latest): $IMAGE_NAME:latest"
docker push $IMAGE_NAME:latest

echo "镜像推送完成！"
echo "注意: latest标签已更新，之前的latest标签已被替换"