# Pretender - 完整方法列表

本文档详细列出了Pretender支持的所有模板变量和方法。

## 📋 目录

- [Faker 方法](#faker-方法)
- [Random 方法](#random-方法)
- [Datetime 方法](#datetime-方法)
- [Date 方法](#date-方法)
- [Time 方法](#time-方法)
- [参数语法说明](#参数语法说明)

## 🎭 Faker 方法

### 👤 个人信息

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
| `{{faker.ssn}}` | 无 | `{{faker.ssn}}` | 生成社会安全号 |

### 🏢 商业信息

| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{faker.company}}` | 无 | `{{faker.company}}` | 生成公司名 |
| `{{faker.job}}` | 无 | `{{faker.job}}` | 生成职位 |
| `{{faker.industry}}` | 无 | `{{faker.industry}}` | 生成行业 |
| `{{faker.company_suffix}}` | 无 | `{{faker.company_suffix}}` | 生成公司后缀 |

### 🔢 数字和ID

| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{faker.uuid4}}` | 无 | `{{faker.uuid4}}` | 生成UUID |
| `{{faker.random_number}}` | digits=8 | `{{faker.random_number:6}}` | 生成随机数字 |
| `{{faker.random_int}}` | 无 | `{{faker.random_int}}` | 生成随机整数 |

### 📅 日期时间

| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{faker.date}}` | 无 | `{{faker.date}}` | 生成日期 |
| `{{faker.time}}` | 无 | `{{faker.time}}` | 生成时间 |
| `{{faker.date_time}}` | 无 | `{{faker.date_time}}` | 生成日期时间 |
| `{{faker.date_time_this_year}}` | 无 | `{{faker.date_time_this_year}}` | 生成今年内的日期时间 |
| `{{faker.date_time_this_month}}` | 无 | `{{faker.date_time_this_month}}` | 生成本月内的日期时间 |
| `{{faker.date_time_this_week}}` | 无 | `{{faker.date_time_this_week}}` | 生成本周内的日期时间 |

### 🌐 网络和文件

| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{faker.url}}` | 无 | `{{faker.url}}` | 生成URL |
| `{{faker.domain_name}}` | 无 | `{{faker.domain_name}}` | 生成域名 |
| `{{faker.ipv4}}` | 无 | `{{faker.ipv4}}` | 生成IPv4地址 |
| `{{faker.ipv6}}` | 无 | `{{faker.ipv6}}` | 生成IPv6地址 |
| `{{faker.file_name}}` | 无 | `{{faker.file_name}}` | 生成文件名 |
| `{{faker.file_extension}}` | 无 | `{{faker.file_extension}}` | 生成文件扩展名 |

### 📝 文本内容

| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{faker.word}}` | 无 | `{{faker.word}}` | 生成单词 |
| `{{faker.sentence}}` | nb_words=6 | `{{faker.sentence:10}}` | 生成句子 |
| `{{faker.paragraph}}` | nb_sentences=3 | `{{faker.paragraph:5}}` | 生成段落 |
| `{{faker.text}}` | max_nb_chars=200 | `{{faker.text:500}}` | 生成文本 |
| `{{faker.lorem}}` | 无 | `{{faker.lorem}}` | 生成Lorem ipsum文本 |

### 🎨 其他

| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{faker.color_name}}` | 无 | `{{faker.color_name}}` | 生成颜色名 |
| `{{faker.hex_color}}` | 无 | `{{faker.hex_color}}` | 生成十六进制颜色 |
| `{{faker.credit_card_number}}` | 无 | `{{faker.credit_card_number}}` | 生成信用卡号 |
| `{{faker.credit_card_expire}}` | 无 | `{{faker.credit_card_expire}}` | 生成信用卡过期日期 |

## 🎲 Random 方法

### 🔢 数字生成

| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{random.randint}}` | 1, 100 | `{{random.randint:10,50}}` | 生成随机整数 |
| `{{random.uniform}}` | 0, 1000 | `{{random.uniform:10.5,99.9}}` | 生成随机浮点数 |
| `{{random.random}}` | 无 | `{{random.random}}` | 生成0-1之间的随机浮点数 |
| `{{random.randrange}}` | 0, 100 | `{{random.randrange:1,10,2}}` | 在指定范围内生成随机整数 |

### 🎯 选择操作

| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{random.choice}}` | ['option1', 'option2', 'option3'] | `{{random.choice:"a","b","c"}}` | 从列表中随机选择元素 |
| `{{random.sample}}` | ['a', 'b', 'c', 'd', 'e'], 3 | `{{random.sample:"1","2","3","4","5":2}}` | 从列表中随机选择多个元素 |
| `{{random.shuffle}}` | 不支持 | - | 不适合在模板中使用 |

### 📊 分布函数

| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{random.gauss}}` | 0, 1 | `{{random.gauss:10,2}}` | 生成高斯分布随机数 |
| `{{random.expovariate}}` | 1.0 | `{{random.expovariate:0.5}}` | 生成指数分布随机数 |
| `{{random.triangular}}` | 0, 1, 0.5 | `{{random.triangular:0,10,5}}` | 生成三角分布随机数 |

## ⏰ Datetime 方法

### 当前时间

| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{datetime.now}}` | 无 | `{{datetime.now}}` | 当前日期时间 |
| `{{datetime.today}}` | 无 | `{{datetime.today}}` | 当前日期 |
| `{{datetime.utcnow}}` | 无 | `{{datetime.utcnow}}` | 当前UTC时间 |

### 时间计算

| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{datetime.date}}` | 无 | `{{datetime.date}}` | 日期对象 |
| `{{datetime.time}}` | 无 | `{{datetime.time}}` | 时间对象 |

### 格式化

| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{datetime.strftime}}` | '%Y-%m-%d %H:%M:%S' | `{{datetime.strftime:"%Y年%m月%d日"}}` | 格式化日期时间 |
| `{{datetime.strptime}}` | 需要两个参数 | `{{datetime.strptime:"2024-01-15":"%Y-%m-%d"}}` | 解析日期时间字符串 |

### 转换方法

| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{datetime.combine}}` | date.today(), time.now() | `{{datetime.combine:date.today:time.now}}` | 组合日期和时间 |
| `{{datetime.fromtimestamp}}` | 当前时间戳 | `{{datetime.fromtimestamp:1642233600}}` | 从时间戳创建 |
| `{{datetime.fromordinal}}` | 当前序数 | `{{datetime.fromordinal:738000}}` | 从序数创建 |
| `{{datetime.fromisoformat}}` | 当前ISO格式 | `{{datetime.fromisoformat:"2024-01-15T10:30:00"}}` | 从ISO格式创建 |

## 📅 Date 方法

### 当前日期

| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{date.today}}` | 无 | `{{date.today}}` | 当前日期 |

### 格式化

| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{date.strftime}}` | '%Y-%m-%d' | `{{date.strftime:"%Y年%m月%d日"}}` | 格式化日期 |
| `{{date.strptime}}` | 需要两个参数 | `{{date.strptime:"2024-01-15":"%Y-%m-%d"}}` | 解析日期字符串 |

### 转换方法

| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{date.fromtimestamp}}` | 当前时间戳 | `{{date.fromtimestamp:1642233600}}` | 从时间戳创建 |
| `{{date.fromordinal}}` | 当前序数 | `{{date.fromordinal:738000}}` | 从序数创建 |
| `{{date.fromisoformat}}` | 当前ISO格式 | `{{date.fromisoformat:"2024-01-15"}}` | 从ISO格式创建 |

## ⏱️ Time 方法

### 当前时间

| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{time.now}}` | 无 | `{{time.now}}` | 当前时间 |

### 格式化

| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{time.strftime}}` | '%H:%M:%S' | `{{time.strftime:"%H时%M分%S秒"}}` | 格式化时间 |
| `{{time.strptime}}` | 需要两个参数 | `{{time.strptime:"10:30:00":"%H:%M:%S"}}` | 解析时间字符串 |

### 转换方法

| 方法 | 默认参数 | 自定义参数示例 | 说明 |
|------|----------|----------------|------|
| `{{time.fromisoformat}}` | 当前ISO格式 | `{{time.fromisoformat:"10:30:00"}}` | 从ISO格式创建 |

## 📝 参数语法说明

### 基本语法

模板变量支持以下格式：

```yaml
# 使用默认参数
{{faker.name}}

# 使用自定义参数
{{faker.random_number:6}}

# 多个参数
{{random.uniform:10,100}}

# 字符串参数
{{random.choice:"option1","option2","option3"}}
```

### 参数类型

#### 数字参数
```yaml
# 整数
{{random.randint:1,100}}

# 浮点数
{{random.uniform:10.5,99.9}}

# 负数
{{random.randint:-100,100}}
```

#### 字符串参数
```yaml
# 简单字符串
{{faker.text:"max_nb_chars":200}}

# 包含特殊字符的字符串
{{random.choice:"Hello World","Test String"}}

# 空字符串
{{random.choice:"","option1","option2"}}
```

#### 布尔参数
```yaml
# true
{{faker.text:"max_nb_chars":200,"fix_exclamation_mark":true}}

# false
{{faker.text:"max_nb_chars":200,"fix_exclamation_mark":false}}
```

### 特殊方法说明

#### Random.choice 和 Random.sample
```yaml
# choice - 参数会被当作列表处理
{{random.choice:"a","b","c"}}

# sample - 需要两个参数：列表和数量
{{random.sample:"1","2","3","4","5":2}}
```

#### Strptime 方法
```yaml
# datetime.strptime - 需要两个参数：日期字符串和格式
{{datetime.strptime:"2024-01-15":"%Y-%m-%d"}}

# date.strptime - 需要两个参数：日期字符串和格式
{{date.strptime:"2024-01-15":"%Y-%m-%d"}}

# time.strptime - 需要两个参数：时间字符串和格式
{{time.strptime:"10:30:00":"%H:%M:%S"}}
```

### 错误处理

当模板变量出现错误时，会返回错误信息：

```yaml
# 方法不存在
{{faker.nonexistent_method}}
# 返回: {{ERROR: faker.nonexistent_method - 'Faker' object has no attribute 'nonexistent_method'}}

# 参数错误
{{random.randint:1}}
# 返回: {{ERROR: random.randint - randint() missing 1 required positional argument: 'b'}}

# 方法不适合在模板中使用
{{random.shuffle}}
# 返回: {{ERROR: shuffle - 不适合在模板中使用}}
```

## 🔗 相关链接

- [Faker 官方文档](https://faker.readthedocs.io/)
- [Python Random 模块](https://docs.python.org/3/library/random.html)
- [Python Datetime 模块](https://docs.python.org/3/library/datetime.html)

---

💡 **提示**: 如果遇到方法不支持或参数错误，请查看错误信息并参考官方文档。 