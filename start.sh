#!/bin/bash

echo "🚀 启动 Pretender 代理服务..."

# 检查依赖
echo "检查 Python 依赖..."
pip install -r requirements.txt

echo "============================================================"
echo "🎯 Pretender - 本地正向代理&Mock服务"
echo "   • 支持URL正则匹配Mock响应"
echo "   • 支持请求头权限验证" 
echo "   • 支持动态数据生成 (Faker)"
echo "   • 支持接口延迟测试"
echo "   • 配置文件热加载"
echo "============================================================"

# 根据参数选择启动方式
if [ "$1" = "dev" ]; then
    echo "📝 开发模式 (支持热重载)"
    hypercorn app:app --bind 0.0.0.0:8888 --reload
elif [ "$1" = "prod" ]; then
    echo "🚀 生产模式 (4个工作进程)"
    hypercorn app:app --bind 0.0.0.0:8888 --workers 4
else
    echo "🎯 默认模式"
    echo "使用方法:"
    echo "  ./start.sh dev   # 开发模式(热重载)"
    echo "  ./start.sh prod  # 生产模式(4个进程)"
    echo ""
    echo "直接启动..."
    hypercorn app:app --bind 0.0.0.0:8888
fi 