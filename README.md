# Pretender - 本地正向代理&Mock服务

> 🚀 一个功能强大的本地HTTP代理服务，支持智能Mock、动态数据生成、接口延迟测试等功能

## ✨ 功能特性

- 🔄 **智能代理转发** - 支持按完整URL正则匹配Mock，未匹配的请求自动转发
- ⚡ **接口延迟测试** - 支持毫秒级精度的延迟模拟，用于性能测试
- 🔐 **请求头验证** - 支持正则匹配的请求头权限验证，失败返回401
- 🎲 **动态数据生成** - 集成Faker库，支持模板变量生成真实数据
- 🔥 **配置文件热更新** - 修改配置文件后自动重新加载，无需重启
- 🐳 **Docker支持** - 提供完整的Docker化部署方案
- 📦 **模块化设计** - 清晰的代码结构，便于维护和扩展

## 📁 项目结构

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

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
# 方式1: 直接运行主入口
python main.py

# 方式2: 运行服务器模块
python -m src.server.proxy_server
```

### 3. 配置代理

将系统或浏览器HTTP代理设置为：`127.0.0.1:8888`

## ⚙️ 配置说明

### 配置文件位置
`config/mock_config.yaml`

### 配置示例

```yaml
mocks:
  # 基础Mock示例
  - url: ^http://www\.baidu\.com/api/rest/v[0-9]$
    method: GET
    headers:
      Authorization: "Bearer.*"  # 支持正则匹配
    response:
      code: 200
      msg:
        desc: "成功"
        zh_CN: "成功"
        zh_TW: "成功"
        en_US: "success"
  
  # 动态数据生成示例 - 使用默认参数
  - url: ^http://www\.example\.com/api/users$
    method: GET
    response:
      code: 200
      msg:
        id: "{{faker.uuid4}}"
        name: "{{faker.name}}"
        email: "{{faker.email}}"
        phone: "{{faker.phone_number}}"
        created_at: "{{faker.date_time_this_year}}"
  
  # 动态数据生成示例 - 使用自定义参数
  - url: ^http://www\.example\.com/api/orders$
    method: GET
    response:
      code: 200
      msg:
        order_id: "ORD-{{faker.random_number:8}}"
        customer_name: "{{faker.name}}"
        total_amount: "{{random.uniform:10,1000}}"
        status: "{{random.choice:\"pending\",\"processing\",\"shipped\"}}"
        created_at: "{{faker.date_time_this_year}}"
  
  # 延迟测试示例
  - url: ^http://www\.sougou1\.com/api/rest/v[0-9]$
    method: GET
    response:
      code: 200
      msg:
        desc: "成功"
        zh_CN: "成功"
        zh_TW: "成功"
        en_US: "success"
      delay: 5000  # 延迟5秒后返回
```

### 配置参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `url` | String | ✅ | 支持正则表达式，使用Python re.fullmatch匹配完整URL |
| `method` | String | ✅ | HTTP方法（GET、POST、PUT、DELETE等） |
| `headers` | Object | ❌ | 请求头验证规则，支持正则匹配 |
| `response` | Object | ✅ | Mock返回内容，支持模板变量 |
| `delay` | Number | ❌ | 模拟接口延迟时间（毫秒） |

## 🎲 数据生成功能

### 支持的模板变量

- `{{faker.method}}` - 使用Faker库生成数据（使用默认参数）
- `{{faker.method:param1,param2}}` - 使用Faker库生成数据（自定义参数）
- `{{random.method}}` - 使用Python random模块（使用默认参数）
- `{{random.method:param1,param2}}` - 使用Python random模块（自定义参数）
- `{{datetime.method}}` - 使用Python datetime模块（使用默认参数）
- `{{datetime.method:param1,param2}}` - 使用Python datetime模块（自定义参数）

### 参数语法说明

- **数字参数**: 直接写数字，如 `{{random.uniform:10,100}}`
- **字符串参数**: 用双引号包围，如 `{{random.choice:"option1","option2"}}`
- **布尔参数**: 使用 `true` 或 `false`，如 `{{faker.text:max_nb_chars:200}}`

### Faker 常用方法

#### 👤 个人信息
| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{faker.name}}` | 无 | `{{faker.name}}` | 生成姓名 |
| `{{faker.first_name}}` | 无 | `{{faker.first_name}}` | 生成名 |
| `{{faker.last_name}}` | 无 | `{{faker.last_name}}` | 生成姓 |
| `{{faker.email}}` | 无 | `{{faker.email}}` | 生成邮箱 |
| `{{faker.phone_number}}` | 无 | `{{faker.phone_number}}` | 生成电话号码 |
| `{{faker.address}}` | 无 | `{{faker.address}}` | 生成完整地址 |
| `{{faker.city}}` | 无 | `{{faker.city}}` | 生成城市名 |
| `{{faker.country}}` | 无 | `{{faker.country}}` | 生成国家名 |
| `{{faker.postcode}}` | 无 | `{{faker.postcode}}` | 生成邮政编码 |

#### 🏢 商业信息
| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{faker.company}}` | 无 | `{{faker.company}}` | 生成公司名 |
| `{{faker.job}}` | 无 | `{{faker.job}}` | 生成职位 |
| `{{faker.industry}}` | 无 | `{{faker.industry}}` | 生成行业 |
| `{{faker.company_suffix}}` | 无 | `{{faker.company_suffix}}` | 生成公司后缀 |

#### 🔢 数字和ID
| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{faker.uuid4}}` | 无 | `{{faker.uuid4}}` | 生成UUID |
| `{{faker.random_number}}` | digits=8 | `{{faker.random_number:6}}` | 生成随机数字 |
| `{{faker.random_int}}` | 无 | `{{faker.random_int}}` | 生成随机整数 |
| `{{faker.ssn}}` | 无 | `{{faker.ssn}}` | 生成社会安全号 |

#### 📅 日期时间
| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{faker.date}}` | 无 | `{{faker.date}}` | 生成日期 |
| `{{faker.time}}` | 无 | `{{faker.time}}` | 生成时间 |
| `{{faker.date_time}}` | 无 | `{{faker.date_time}}` | 生成日期时间 |
| `{{faker.date_time_this_year}}` | 无 | `{{faker.date_time_this_year}}` | 生成今年内的日期时间 |
| `{{faker.date_time_this_month}}` | 无 | `{{faker.date_time_this_month}}` | 生成本月内的日期时间 |
| `{{faker.date_time_this_week}}` | 无 | `{{faker.date_time_this_week}}` | 生成本周内的日期时间 |

#### 🌐 网络和文件
| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{faker.url}}` | 无 | `{{faker.url}}` | 生成URL |
| `{{faker.domain_name}}` | 无 | `{{faker.domain_name}}` | 生成域名 |
| `{{faker.ipv4}}` | 无 | `{{faker.ipv4}}` | 生成IPv4地址 |
| `{{faker.ipv6}}` | 无 | `{{faker.ipv6}}` | 生成IPv6地址 |
| `{{faker.file_name}}` | 无 | `{{faker.file_name}}` | 生成文件名 |
| `{{faker.file_extension}}` | 无 | `{{faker.file_extension}}` | 生成文件扩展名 |

#### 📝 文本内容
| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{faker.word}}` | 无 | `{{faker.word}}` | 生成单词 |
| `{{faker.sentence}}` | nb_words=6 | `{{faker.sentence:10}}` | 生成句子 |
| `{{faker.paragraph}}` | nb_sentences=3 | `{{faker.paragraph:5}}` | 生成段落 |
| `{{faker.text}}` | max_nb_chars=200 | `{{faker.text:500}}` | 生成文本 |
| `{{faker.lorem}}` | 无 | `{{faker.lorem}}` | 生成Lorem ipsum文本 |

#### 🎨 其他
| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{faker.color_name}}` | 无 | `{{faker.color_name}}` | 生成颜色名 |
| `{{faker.hex_color}}` | 无 | `{{faker.hex_color}}` | 生成十六进制颜色 |
| `{{faker.credit_card_number}}` | 无 | `{{faker.credit_card_number}}` | 生成信用卡号 |
| `{{faker.credit_card_expire}}` | 无 | `{{faker.credit_card_expire}}` | 生成信用卡过期日期 |

### Random 常用方法

#### 🔢 数字生成
| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{random.randint}}` | 1, 100 | `{{random.randint:10,50}}` | 生成随机整数 |
| `{{random.uniform}}` | 0, 1000 | `{{random.uniform:10.5,99.9}}` | 生成随机浮点数 |
| `{{random.random}}` | 无 | `{{random.random}}` | 生成0-1之间的随机浮点数 |
| `{{random.randrange}}` | 0, 100 | `{{random.randrange:1,10,2}}` | 在指定范围内生成随机整数 |

#### 🎯 选择操作
| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{random.choice}}` | ['option1', 'option2', 'option3'] | `{{random.choice:"a","b","c"}}` | 从列表中随机选择元素 |
| `{{random.sample}}` | ['a', 'b', 'c', 'd', 'e'], 3 | `{{random.sample:"1","2","3","4","5":2}}` | 从列表中随机选择多个元素 |
| `{{random.shuffle}}` | 不支持 | - | 不适合在模板中使用 |

#### 📊 分布函数
| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{random.gauss}}` | 0, 1 | `{{random.gauss:10,2}}` | 生成高斯分布随机数 |
| `{{random.expovariate}}` | 1.0 | `{{random.expovariate:0.5}}` | 生成指数分布随机数 |
| `{{random.triangular}}` | 0, 1, 0.5 | `{{random.triangular:0,10,5}}` | 生成三角分布随机数 |

### Datetime 常用方法

#### ⏰ 当前时间
| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{datetime.now}}` | 无 | `{{datetime.now}}` | 当前日期时间 |
| `{{datetime.today}}` | 无 | `{{datetime.today}}` | 当前日期 |
| `{{datetime.utcnow}}` | 无 | `{{datetime.utcnow}}` | 当前UTC时间 |

#### ⏱️ 时间计算
| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{datetime.timedelta}}` | days=1 | `{{datetime.timedelta:7}}` | 时间间隔 |
| `{{datetime.date}}` | 无 | `{{datetime.date}}` | 日期对象 |
| `{{datetime.time}}` | 无 | `{{datetime.time}}` | 时间对象 |

#### 📅 格式化
| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{datetime.strftime}}` | '%Y-%m-%d %H:%M:%S' | `{{datetime.strftime:"%Y年%m月%d日"}}` | 格式化日期时间 |
| `{{datetime.strptime}}` | 需要两个参数 | `{{datetime.strptime:"2024-01-15":"%Y-%m-%d"}}` | 解析日期时间字符串 |

## 📚 相关文档

### 🔗 官方文档
- **[Faker GitHub](https://github.com/joke2k/faker)** - Faker项目主页
- **[Faker PyPI](https://pypi.org/project/Faker/)** - Faker包信息
- **[Faker 官方文档](https://faker.readthedocs.io/)** - 完整使用指南
- **[Faker Providers](https://faker.readthedocs.io/en/master/providers.html)** - 所有可用Providers

### 🐍 Python 官方文档
- **[Random 模块](https://docs.python.org/3/library/random.html)** - 随机数生成
- **[Datetime 模块](https://docs.python.org/3/library/datetime.html)** - 日期时间处理

### 🛠️ 在线工具
- **[正则表达式测试](https://regex101.com/)** - 测试正则表达式
- **[JSON 格式化](https://jsonformatter.curiousconcept.com/)** - JSON格式化和验证
- **[YAML 验证](https://www.yamllint.com/)** - YAML语法检查

## 🧪 测试示例

### 基础Mock测试
```bash
# 验证通过 - 返回mock
curl -x http://127.0.0.1:8888 -H "Authorization: Bearer token123" http://www.baidu.com/api/rest/v1
# 返回：{"desc":"成功","zh_CN":"成功","zh_TW":"成功","en_US":"success"}

# 验证失败 - 返回401异常
curl -x http://127.0.0.1:8888 http://www.baidu.com/api/rest/v1
# 返回：{"error":"unauthorized","message":"Header validation failed: Authorization=, expected pattern: Bearer.*","code":401}
```

### 动态数据生成测试
```bash
# 用户数据生成（使用默认参数）
curl -x http://127.0.0.1:8888 http://www.example.com/api/users
# 返回：{"id":"550e8400-e29b-41d4-a716-446655440000","name":"张三","email":"zhangsan@example.com","phone":"13812345678","created_at":"2024-01-15T10:30:00"}

# 订单数据生成（使用自定义参数）
curl -x http://127.0.0.1:8888 http://www.example.com/api/orders
# 返回：{"order_id":"ORD-12345678","customer_name":"李四","total_amount":1234.56,"status":"pending","created_at":"2024-01-15T10:30:00"}
```

### 延迟测试
```bash
# 延迟测试
curl -x http://127.0.0.1:8888 http://www.sougou1.com/api/rest/v1
# 延迟5秒后返回：{"desc":"成功","zh_CN":"成功","zh_TW":"成功","en_US":"success"}
```

## 🏗️ 模块说明

### 📁 src/core/
- **config_manager.py** - 配置管理，支持热更新和header验证
- **data_generator.py** - 数据生成，支持Faker和模板变量

### 📁 src/handlers/
- **response_handler.py** - 响应处理，包括mock、代理和401响应

### 📁 src/server/
- **proxy_server.py** - 代理服务器，HTTP请求处理

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