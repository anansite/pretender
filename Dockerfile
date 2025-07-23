FROM python:3.11-slim

WORKDIR /app

# 复制依赖文件
COPY requirements.txt ./

# 安装依赖
RUN apt-get update && apt-get upgrade -y && apt-get clean && pip install --no-cache-dir -r requirements.txt

# 复制源代码和配置文件
COPY src/ ./src/
COPY main.py ./
COPY config/ ./config/

EXPOSE 8888

CMD ["python", "main.py"] 