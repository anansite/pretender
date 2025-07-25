FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖和时区配置
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt ./

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码和配置文件
COPY src/ ./src/
COPY app.py ./
COPY config/ ./config/



# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
# 设置时区为Asia/Shanghai
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

EXPOSE 8888

# 直接使用hypercorn启动，2个worker进程
CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:8888", "--workers", "2"] 