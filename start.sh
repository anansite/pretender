#!/bin/bash

echo "启动 Pretender 代理服务..."

# 检查依赖
echo "检查 Python 依赖..."
pip install -r requirements.txt

echo "============================================================"
echo "Pretender - 本地正向代理&Mock服务"
echo "   • 支持 HTTP / HTTPS (MITM) 代理"
echo "   • 支持 URL 正则匹配 Mock 响应"
echo "   • 支持请求头权限验证"
echo "   • 支持动态数据生成 (Faker)"
echo "   • 支持接口延迟测试"
echo "   • 配置文件热加载"
echo "============================================================"

echo "启动代理服务器..."
python app.py
