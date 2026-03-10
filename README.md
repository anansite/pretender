# Pretender - 本地正向代理&Mock服务

> 一个功能强大的本地代理服务，支持 HTTP/HTTPS(MITM) 智能Mock、动态数据生成、接口延迟测试等功能

## 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [HTTPS 代理](#https-代理)
- [配置指南](#配置指南)
- [数据生成](#数据生成)
- [使用示例](#使用示例)
- [部署指南](#部署指南)
- [常见问题](#常见问题)
- [API参考](#api参考)
- [相关文档](#相关文档)

---

## 功能特性

| 功能 | 描述 | 示例 |
|------|------|------|
| **HTTP 代理** | 支持按完整URL正则匹配Mock，未匹配的请求自动转发 | `^http://api\.example\.com/.*$` |
| **HTTPS MITM 代理** | 通过动态证书签发拦截HTTPS请求，支持Mock和转发 | `^https://api\.example\.com/.*$` |
| **接口延迟测试** | 支持毫秒级精度的延迟模拟，用于性能测试 | `delay: 3000` |
| **请求头验证** | 支持正则匹配的请求头权限验证，失败返回401 | `Authorization: "Bearer.*"` |
| **动态数据生成** | 集成Faker库，支持模板变量生成真实数据 | `{{faker.name}}` |
| **配置文件热更新** | 修改配置文件后自动重新加载，无需重启 | 实时生效 |
| **Docker支持** | 提供完整的Docker化部署方案 | 一键部署 |

---

## 快速开始

### Docker部署（推荐）

#### 使用预构建镜像

```bash
# 1. 运行容器
docker run -d -p 8888:8888 jsonstiananan/pretender-proxy:latest

# 2. 测试 HTTP Mock
curl -x http://127.0.0.1:8888 http://www.example.com/api/test
```

#### 挂载自定义配置

```bash
# 运行容器（挂载配置目录）
docker run -d -p 8888:8888 -v ./mockConfig:/app/config jsonstiananan/pretender-proxy:latest
```

### 源码运行

```bash
# 1. 克隆项目
git clone https://github.com/anansite/pretender.git
cd pretender

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
python app.py

# 或使用便捷脚本
./start.sh
```

启动后日志会打印 CA 证书路径，HTTPS Mock 需客户端信任该证书。

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PRETENDER_HOST` | `0.0.0.0` | 监听地址 |
| `PRETENDER_PORT` | `8888` | 监听端口 |

---

## HTTPS 代理

Pretender 通过 MITM（中间人）方式拦截 HTTPS 请求：

1. 客户端发送 `CONNECT host:port` 请求
2. 代理用自签名 CA 动态签发域名/IP 证书
3. 与客户端完成 TLS 握手后读取明文 HTTP 请求
4. 匹配 Mock 规则或转发到真实服务器

### 信任 CA 证书

首次启动时会自动生成 CA 证书（`certs/ca.crt`）。Docker 环境可通过以下方式导出：

```bash
docker cp <container>:/app/certs/ca.crt ~/pretender-ca.crt
```

#### macOS

```bash
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain ~/pretender-ca.crt
```

#### curl（临时使用）

```bash
# 方式1：指定 CA 证书
curl -x http://127.0.0.1:8888 --cacert certs/ca.crt https://api.example.com/api/test

# 方式2：跳过证书验证
curl -k -x http://127.0.0.1:8888 https://api.example.com/api/test
```

### HTTPS Mock 配置示例

```yaml
mocks:
  # HTTPS Mock（URL以https://开头）
  - url: ^https://api\.example\.com/api/test$
    method: GET
    response:
      code: 200
      msg:
        message: "Hello from HTTPS Mock!"
        timestamp: "{{datetime.now}}"

  # 支持 IP 地址 + 非标准端口
  - url: ^https://172\.25\.224\.105:11111/api/rest/.*$
    method: GET
    response:
      code: 200
      msg:
        data: "HTTPS Mock Response"
```

---

## 配置指南

### 配置文件位置

`config/mock_config.yaml`

### 配置结构

```yaml
mocks:
  - url: "^https?://example\.com/api/.*$"  # 正则匹配URL（支持http/https）
    method: "GET"                           # HTTP方法
    headers:                                # 请求头验证（可选）
      Authorization: "Bearer.*"
    response:                               # 响应配置
      code: 200                             # HTTP状态码
      msg:                                  # 响应内容
        message: "{{faker.sentence}}"
        data: "{{random.randint:1,100}}"
      delay: 1000                           # 延迟时间（毫秒，可选）
```

### 配置参数说明

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `url` | String | 是 | 正则表达式，`re.fullmatch` 匹配完整URL | `^https?://api\.example\.com/.*$` |
| `method` | String | 是 | HTTP方法（GET、POST、PUT、DELETE等） | `GET` |
| `headers` | Object | 否 | 请求头验证规则，支持正则匹配 | `Authorization: "Bearer.*"` |
| `response` | Object | 是 | Mock返回内容，支持模板变量 | 见示例 |
| `delay` | Number | 否 | 模拟接口延迟时间（毫秒） | `3000` |

### 常用配置示例

#### 基础Mock

```yaml
- url: ^http://api\.example\.com/users$
  method: GET
  response:
    code: 200
    msg:
      id: "{{faker.uuid4}}"
      name: "{{faker.name}}"
```

#### 带验证的Mock

```yaml
- url: ^http://api\.example\.com/secure$
  method: GET
  headers:
    Authorization: "Bearer.*"
  response:
    code: 200
    msg:
      message: "认证成功"
```

#### 延迟测试

```yaml
- url: ^http://api\.example\.com/slow$
  method: GET
  response:
    code: 200
    msg:
      message: "延迟响应"
    delay: 3000  # 延迟3秒
```

---

## 数据生成

### 模板变量语法

| 类型 | 语法 | 示例 |
|------|------|------|
| **Faker** | `{{faker.method}}` | `{{faker.name}}` |
| **Faker带参数** | `{{faker.method:param1,param2}}` | `{{faker.random_number:6}}` |
| **Random** | `{{random.method}}` | `{{random.randint:1,100}}` |
| **Datetime** | `{{datetime.method}}` | `{{datetime.now}}` |

### 常用方法速查

#### Faker 常用方法

| 方法 | 示例 | 说明 |
|------|------|------|
| `{{faker.name}}` | `张三` | 生成姓名 |
| `{{faker.email}}` | `zhangsan@example.com` | 生成邮箱 |
| `{{faker.phone_number}}` | `13812345678` | 生成电话号码 |
| `{{faker.uuid4}}` | `550e8400-e29b-41d4-...` | 生成UUID |
| `{{faker.company}}` | `腾讯科技有限公司` | 生成公司名 |
| `{{faker.address}}` | `北京市朝阳区xxx街道` | 生成地址 |

#### Random 常用方法

| 方法 | 示例 | 说明 |
|------|------|------|
| `{{random.randint:1,100}}` | `42` | 随机整数 |
| `{{random.uniform:10,100}}` | `67.89` | 随机浮点数 |
| `{{random.choice:"a","b","c"}}` | `b` | 随机选择 |

#### Datetime 常用方法

| 方法 | 示例 | 说明 |
|------|------|------|
| `{{datetime.now}}` | `2024-01-15 10:30:00` | 当前日期时间 |
| `{{datetime.strftime:"%Y-%m-%d"}}` | `2024-01-15` | 格式化日期 |

---

## 使用示例

### HTTP Mock

```bash
# Mock 响应
curl -x http://127.0.0.1:8888 http://www.example.com/api/test

# 代理转发（未匹配Mock规则）
curl -x http://127.0.0.1:8888 http://httpbin.org/get
```

### HTTPS Mock

```bash
# 使用 CA 证书
curl -x http://127.0.0.1:8888 --cacert certs/ca.crt https://api.example.com/api/test

# 跳过证书验证
curl -k -x http://127.0.0.1:8888 https://api.example.com/api/test

# HTTPS 透传（未匹配，转发到真实服务器）
curl -k -x http://127.0.0.1:8888 https://httpbin.org/get
```

### 各语言代理配置

#### Java

```bash
-Dhttp.proxyHost=localhost -Dhttp.proxyPort=8888
-Dhttps.proxyHost=localhost -Dhttps.proxyPort=8888
```

#### Python

```python
import os
os.environ['HTTP_PROXY'] = 'http://localhost:8888'
os.environ['HTTPS_PROXY'] = 'http://localhost:8888'
```

#### Node.js

```javascript
process.env.HTTP_PROXY = 'http://localhost:8888';
process.env.HTTPS_PROXY = 'http://localhost:8888';
```

---

## 部署指南

### Docker

```bash
# 基础运行
docker run -d -p 8888:8888 jsonstiananan/pretender-proxy:latest

# 挂载配置 + 持久化证书
docker run -d -p 8888:8888 \
  -v ./mockConfig:/app/config \
  -v ./certs:/app/certs \
  jsonstiananan/pretender-proxy:latest

# 导出 CA 证书
docker cp <container>:/app/certs/ca.crt .
```

### 源码

```bash
pip install -r requirements.txt
python app.py
```

---

## 常见问题

### 配置相关

| 问题 | 解决方案 |
|------|----------|
| 如何修改Mock配置？ | 编辑 `config/mock_config.yaml`，保存后自动重新加载 |
| 代理配置不生效？ | 检查代理地址是否为 `127.0.0.1:8888`，确保服务正在运行 |
| 数据生成模板不工作？ | 检查模板语法，确保使用双大括号 `{{}}`，验证方法名和参数格式 |

### HTTPS 相关

| 问题 | 解决方案 |
|------|----------|
| HTTPS 请求失败？ | 客户端需信任 `certs/ca.crt`，或使用 `curl -k` 跳过验证 |
| 证书在哪里？ | 首次启动自动生成在 `certs/` 目录，Docker 中为 `/app/certs/` |
| IP 地址的 HTTPS？ | 已支持，证书 SAN 会自动使用 IPAddress 类型 |

### Docker 相关

| 问题 | 解决方案 |
|------|----------|
| 容器无法启动？ | 检查端口8888是否被占用，查看日志：`docker logs <container>` |
| 配置文件不生效？ | 检查挂载：`docker exec <container> ls -la /app/config/` |
| 证书丢失（重启后）？ | 挂载证书目录：`-v ./certs:/app/certs` |

---

## API参考

### 项目结构

```
pretender/
├── app.py                        # 主入口（asyncio 事件循环）
├── requirements.txt              # 依赖
├── Dockerfile
├── start.sh
├── config/
│   └── mock_config.yaml          # Mock 配置
├── certs/                        # 自动生成
│   ├── ca.key                    # Root CA 私钥
│   ├── ca.crt                    # Root CA 证书（客户端需信任）
│   └── domains/                  # 域名证书缓存
└── src/
    ├── core/
    │   ├── config_manager.py     # 配置管理（热更新）
    │   ├── cert_manager.py       # CA + 域名证书签发
    │   └── data_generator.py     # 模板数据生成
    ├── handlers/
    │   └── response_handler.py   # Legacy 同步响应处理
    └── server/
        ├── async_proxy.py        # asyncio TCP 代理（HTTP + HTTPS MITM）
        └── proxy_server.py       # Legacy 同步代理服务器
```

### 请求流程

```
Client → Proxy(8888)
  ├─ HTTP:    解析URL → 噪音过滤 → match_mock()
  │             ├─ 匹配 → DataGenerator → Mock JSON 响应
  │             └─ 未匹配 → httpx 转发 → 真实服务器
  └─ CONNECT: 动态签发证书 → TLS 握手 → 读取明文请求 → 同上流程
```

---

## 相关文档

| 文档 | 说明 |
|------|------|
| [Faker 官方文档](https://faker.readthedocs.io/) | 数据生成库 |
| [Python Random 模块](https://docs.python.org/3/library/random.html) | 随机数生成 |
| [Python Datetime 模块](https://docs.python.org/3/library/datetime.html) | 日期时间处理 |
| [正则表达式测试](https://regex101.com/) | URL匹配规则调试 |

---

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情
