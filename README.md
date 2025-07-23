# Pretender - 本地正向代理&Mock服务

> 🚀 一个功能强大的本地HTTP代理服务，支持智能Mock、动态数据生成、接口延迟测试等功能

## 📋 目录

- [功能特性](#-功能特性)
- [快速开始](#-快速开始)
- [配置指南](#️-配置指南)
- [部署方式](#-部署方式)
- [数据生成](#-数据生成)
- [使用示例](#-使用示例)
- [常见问题](#-常见问题)
- [API参考](#-api参考)
- [相关文档](#-相关文档)

## ✨ 功能特性

- 🔄 **智能代理转发** - 支持按完整URL正则匹配Mock，未匹配的请求自动转发
- ⚡ **接口延迟测试** - 支持毫秒级精度的延迟模拟，用于性能测试
- 🔐 **请求头验证** - 支持正则匹配的请求头权限验证，失败返回401
- 🎲 **动态数据生成** - 集成Faker库，支持模板变量生成真实数据
- 🔥 **配置文件热更新** - 修改配置文件后自动重新加载，无需重启
- 🐳 **Docker支持** - 提供完整的Docker化部署方案
- 📦 **模块化设计** - 清晰的代码结构，便于维护和扩展

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip 包管理器

### 1. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd pretender

# 安装依赖
pip install -r requirements.txt
```

### 2. 创建配置文件

```bash
# 创建配置目录
mkdir -p config

# 创建基础配置文件
cat > config/mock_config.yaml << 'EOF'
mocks:
  # 测试配置
  - url: ^http://www\.example\.com/api/test$
    method: GET
    response:
      code: 200
      msg:
        message: "Hello Pretender!"
        timestamp: "{{datetime.now}}"
EOF
```

### 3. 启动服务

```bash
# 方式1: 直接运行主入口
python main.py

# 方式2: 运行服务器模块
python -m src.server.proxy_server
```

### 4. 配置代理

将系统或浏览器HTTP代理设置为：`127.0.0.1:8888`

### 5. 测试验证

```bash
# 测试Mock功能
curl -x http://127.0.0.1:8888 http://www.example.com/api/test

# 测试代理转发
curl -x http://127.0.0.1:8888 http://httpbin.org/get
```

## ⚙️ 配置指南

### 配置文件位置
`config/mock_config.yaml`

### 配置结构

```yaml
mocks:
  - url: "^http://example\.com/api/.*$"    # 正则匹配URL
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

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `url` | String | ✅ | 支持正则表达式，使用Python re.fullmatch匹配完整URL |
| `method` | String | ✅ | HTTP方法（GET、POST、PUT、DELETE等） |
| `headers` | Object | ❌ | 请求头验证规则，支持正则匹配 |
| `response` | Object | ✅ | Mock返回内容，支持模板变量 |
| `delay` | Number | ❌ | 模拟接口延迟时间（毫秒） |

### 常用配置示例

#### 基础Mock
```yaml
- url: ^http://api\.example\.com/users$
  method: GET
  response:
    code: 200
    msg:
      users: [
        {"id": "{{faker.uuid4}}", "name": "{{faker.name}}"},
        {"id": "{{faker.uuid4}}", "name": "{{faker.name}}"}
      ]
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

## 🐳 部署方式

### Docker 部署

#### 使用预构建镜像（推荐）

```bash
# 创建配置目录
mkdir mockConfig && cp config/mock_config.yaml mockConfig/

# 运行容器
docker run -d -p 8888:8888 -v ./mockConfig:/app/config jsonstiananan/pretender-proxy:latest
```

#### 构建自定义镜像

```bash
# 构建镜像
docker build -t pretender-proxy .

# 运行容器
docker run -d -p 8888:8888 pretender-proxy
```

### 各语言配置

#### Java 项目

```bash
# bootRun 方式
jvmArgs = [...,
           "-Dhttp.proxyHost=localhost",
           "-Dhttp.proxyPort=8888",
]

# 应用程序配置
http.proxyHost=localhost
http.proxyPort=8888

# 代码设置
System.setProperty("http.proxyHost", "localhost");
System.setProperty("http.proxyPort", "8888");
```

#### Python 项目

```python
import os
os.environ['HTTP_PROXY'] = 'http://localhost:8888'
os.environ['HTTPS_PROXY'] = 'http://localhost:8888'
```

#### Node.js 项目

```javascript
process.env.HTTP_PROXY = 'http://localhost:8888';
process.env.HTTPS_PROXY = 'http://localhost:8888';
```

#### 浏览器配置

1. **Chrome/Edge**: 设置 → 高级 → 系统 → 打开计算机代理设置
2. **Firefox**: 设置 → 网络设置 → 手动配置代理
3. **Safari**: 偏好设置 → 高级 → 代理

## 🎲 数据生成

### 模板变量语法

支持以下格式的模板变量：

- `{{faker.method}}` - 使用Faker库生成数据（默认参数）
- `{{faker.method:param1,param2}}` - 使用Faker库生成数据（自定义参数）
- `{{random.method}}` - 使用Python random模块（默认参数）
- `{{random.method:param1,param2}}` - 使用Python random模块（自定义参数）
- `{{datetime.method}}` - 使用Python datetime模块（默认参数）
- `{{datetime.method:param1,param2}}` - 使用Python datetime模块（自定义参数）

### 参数语法

- **数字参数**: 直接写数字，如 `{{random.uniform:10,100}}`
- **字符串参数**: 用双引号包围，如 `{{random.choice:"option1","option2"}}`
- **布尔参数**: 使用 `true` 或 `false`

### 常用方法速查

#### Faker 常用方法
| 方法 | 示例 | 说明 |
|------|------|------|
| `{{faker.name}}` | `张三` | 生成姓名 |
| `{{faker.email}}` | `zhangsan@example.com` | 生成邮箱 |
| `{{faker.phone_number}}` | `13812345678` | 生成电话号码 |
| `{{faker.uuid4}}` | `550e8400-e29b-41d4-a716-446655440000` | 生成UUID |
| `{{faker.company}}` | `腾讯科技有限公司` | 生成公司名 |
| `{{faker.address}}` | `北京市朝阳区xxx街道` | 生成地址 |

#### Random 常用方法
| 方法 | 示例 | 说明 |
|------|------|------|
| `{{random.randint:1,100}}` | `42` | 生成随机整数 |
| `{{random.uniform:10,100}}` | `67.89` | 生成随机浮点数 |
| `{{random.choice:"a","b","c"}}` | `b` | 从列表中随机选择 |

#### Datetime 常用方法
| 方法 | 示例 | 说明 |
|------|------|------|
| `{{datetime.now}}` | `2024-01-15 10:30:00` | 当前日期时间 |
| `{{datetime.strftime:"%Y-%m-%d"}}` | `2024-01-15` | 格式化日期 |

### 完整方法列表

> 📚 **详细方法文档**: 查看 [完整方法列表](METHODS.md) 获取所有支持的方法和参数说明。

## 🧪 使用示例

### 基础Mock测试

```bash
# 测试Mock响应
curl -x http://127.0.0.1:8888 http://www.example.com/api/test
# 返回: {"message":"Hello Pretender!","timestamp":"2024-01-15 10:30:00"}

# 测试代理转发
curl -x http://127.0.0.1:8888 http://httpbin.org/get
# 返回: 原始响应内容
```

### 动态数据生成测试

```bash
# 用户数据生成
curl -x http://127.0.0.1:8888 http://api.example.com/users
# 返回: {"users":[{"id":"550e8400-e29b-41d4-a716-446655440000","name":"张三"}]}

# 订单数据生成
curl -x http://127.0.0.1:8888 http://api.example.com/orders
# 返回: {"order_id":"ORD-12345678","total_amount":1234.56,"status":"pending"}
```

### 延迟测试

```bash
# 延迟响应测试
curl -x http://127.0.0.1:8888 http://api.example.com/slow
# 延迟3秒后返回: {"message":"延迟响应"}
```

## ❓ 常见问题

### Q: 如何修改Mock配置？
A: 编辑 `config/mock_config.yaml` 文件，保存后会自动重新加载配置。

### Q: 代理配置不生效？
A: 检查以下几点：
- 确保代理地址为 `127.0.0.1:8888`
- 确保服务正在运行
- 检查防火墙设置

### Q: 数据生成模板不工作？
A: 检查模板语法：
- 确保使用双大括号 `{{}}`
- 检查方法名是否正确
- 验证参数格式

### Q: 如何查看详细日志？
A: 启动时添加调试参数：
```bash
python main.py --debug
```

### Q: Docker容器无法启动？
A: 检查以下几点：
- 确保端口8888未被占用
- 检查配置文件权限
- 查看容器日志：`docker logs <container-id>`

## 📚 API参考

### 项目结构

```
pretender/
├── 📄 main.py                    # 主入口文件
├── 📄 README.md                  # 说明文档
├── 📄 requirements.txt           # 依赖文件
├── 🐳 Dockerfile                # Docker配置
├── 📁 config/
│   └── 📄 mock_config.yaml     # 配置文件
└── 📁 src/                      # 源代码目录
    ├── 📄 __init__.py
    ├── 📁 core/                 # 核心功能模块
    │   ├── 📄 __init__.py
    │   ├── 📄 config_manager.py # 配置管理
    │   └── 📄 data_generator.py # 数据生成
    ├── 📁 handlers/             # 处理器模块
    │   ├── 📄 __init__.py
    │   └── 📄 response_handler.py # 响应处理
    └── 📁 server/               # 服务器模块
        ├── 📄 __init__.py
        └── 📄 proxy_server.py   # 代理服务器
```

### 核心模块

#### 📁 src/core/
- **config_manager.py** - 配置管理，支持热更新和header验证
- **data_generator.py** - 数据生成，支持Faker和模板变量

#### 📁 src/handlers/
- **response_handler.py** - 响应处理，包括mock、代理和401响应

#### 📁 src/server/
- **proxy_server.py** - 代理服务器，HTTP请求处理

## 📖 相关文档

### 🔗 官方文档
- **[Faker 官方文档](https://faker.readthedocs.io/)** - 完整使用指南
- **[Python Random 模块](https://docs.python.org/3/library/random.html)** - 随机数生成
- **[Python Datetime 模块](https://docs.python.org/3/library/datetime.html)** - 日期时间处理

### 🛠️ 在线工具
- **[正则表达式测试](https://regex101.com/)** - 测试正则表达式
- **[JSON 格式化](https://jsonformatter.curiousconcept.com/)** - JSON格式化和验证
- **[YAML 验证](https://www.yamllint.com/)** - YAML语法检查

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

💡 **提示**: 如需自定义mock规则，编辑 `config/mock_config.yaml` 即可，支持热更新！ 