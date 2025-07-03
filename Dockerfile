FROM python:3.11-slim

WORKDIR /app

COPY proxy_mock_server.py ./
COPY config ./
RUN apt-get update && apt-get upgrade -y && apt-get clean && pip install --no-cache-dir httpx pyyaml

# 配置文件通过挂载方式提供
# docker run -v $PWD/mock_config.yaml:/app/mock_config.yaml ...

EXPOSE 8888

CMD ["python", "proxy_mock_server.py"] 