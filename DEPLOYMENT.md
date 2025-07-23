# Pretender - 部署指南

> 🚀 详细的部署指南，包含Docker部署、各语言配置、故障排除等内容

## 📋 目录

- [🐳 Docker部署](#-docker部署)
- [🔧 各语言配置](#-各语言配置)
- [🔍 故障排除](#-故障排除)
- [📚 高级用法](#-高级用法)

---

## 🐳 Docker部署

### 🚀 快速开始

#### 使用预构建镜像（推荐）

```bash
# 1️⃣ 运行容器（使用默认配置）
docker run -d -p 8888:8888 jsonstiananan/pretender-proxy:latest

# 2️⃣ 配置代理
# 将系统或浏览器HTTP代理设置为：127.0.0.1:8888

# 3️⃣ 测试验证
curl -x http://127.0.0.1:8888 http://www.example.com/api/test
```

#### 挂载自定义配置

```bash
# 1️⃣ 创建配置目录
mkdir mockConfig && cp config/mock_config.yaml mockConfig/

# 2️⃣ 运行容器
docker run -d -p 8888:8888 -v ./mockConfig:/app/config jsonstiananan/pretender-proxy:latest

# 3️⃣ 配置代理
# 将系统或浏览器HTTP代理设置为：127.0.0.1:8888

# 4️⃣ 测试验证
curl -x http://127.0.0.1:8888 http://www.example.com/api/test
```

### 🔧 构建自定义镜像

```bash
# 进入项目目录
cd pretender

# 构建镜像
docker build -t pretender-proxy .

# 运行容器
docker run -d -p 8888:8888 pretender-proxy
```

### 📚 Docker使用指南

#### 🔧 容器管理

```bash
# 查看容器状态
docker ps

# 查看实时日志
docker logs -f pretender-proxy

# 进入容器
docker exec -it pretender-proxy /bin/bash

# 停止容器
docker stop pretender-proxy
```

#### 🧪 测试验证

```bash
# 测试基础Mock
curl -x http://127.0.0.1:8888 http://www.example.com/api/test

# 测试中文数据生成
curl -x http://127.0.0.1:8888 http://www.test.com/api/chinese

# 测试代理转发
curl -x http://127.0.0.1:8888 http://httpbin.org/get
```

#### 🔍 故障排除

```bash
# 查看详细错误信息
docker logs pretender-proxy

# 前台运行查看启动信息
docker run -it -p 8888:8888 pretender-proxy

# 检查配置文件
docker exec pretender-proxy cat /app/config/mock_config.yaml
```

---

## 🔍 故障排除

### 🤔 配置相关

| 问题 | 解决方案 |
|------|----------|
| **如何修改Mock配置？** | 编辑 `config/mock_config.yaml` 文件，保存后会自动重新加载配置 |
| **代理配置不生效？** | 检查代理地址是否为 `127.0.0.1:8888`，确保服务正在运行 |
| **数据生成模板不工作？** | 检查模板语法，确保使用双大括号 `{{}}`，验证方法名和参数格式 |

### 🐳 Docker相关

| 问题 | 解决方案 |
|------|----------|
| **Docker容器无法启动？** | 检查端口8888是否被占用，查看容器日志：`docker logs <container-id>` |
| **启动信息不显示？** | 使用 `docker logs -f pretender-proxy` 查看实时日志 |
| **配置文件不生效？** | 检查配置文件是否正确挂载：`docker exec pretender-proxy ls -la /app/config/` |

### 🔧 调试相关

| 问题 | 解决方案 |
|------|----------|
| **如何查看详细日志？** | 启动时添加调试参数：`python main.py --debug` |
| **中文显示问题？** | 检查容器日志中的编码信息：`docker logs pretender-proxy \| grep -i encoding` |

---

## 📚 高级用法

### 🐳 多容器部署

```bash
# 创建Docker网络
docker network create pretender-net

# 运行多个实例
docker run -d --name pretender-1 --network pretender-net -p 8888:8888 pretender-proxy
docker run -d --name pretender-2 --network pretender-net -p 8889:8888 pretender-proxy
```

### 🔧 环境变量配置

```bash
# 使用环境变量配置
docker run -d -p 8888:8888 \
  -e PYTHONPATH=/app \
  -v ./my-config:/app/config \
  pretender-proxy
```

### 💾 数据卷持久化

```bash
# 创建数据卷
docker volume create pretender-config

# 使用数据卷
docker run -d -p 8888:8888 \
  -v pretender-config:/app/config \
  pretender-proxy
```

### 🎯 最佳实践

1. **开发环境**: 使用默认配置快速开始
2. **测试环境**: 挂载测试配置文件
3. **生产环境**: 挂载生产配置文件，使用数据卷持久化
4. **配置文件**: 使用版本控制管理配置文件
5. **监控**: 定期查看容器日志和状态

---

💡 **提示**: 修改配置文件后，服务会自动重新加载，无需重启容器！ 