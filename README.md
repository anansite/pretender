# Pretender 本地正向代理&Mock服务

## 功能简介
- 作为本地HTTP代理，支持按完整URL正则mock返回，否则自动转发到目标地址。

## 依赖安装
```bash
pip install httpx pyyaml
```

## 启动方式
```bash
python3 proxy_mock_server.py
```
默认监听 8888 端口。将系统或浏览器HTTP代理设置为127.0.0.1:8888。

## 配置文件示例（pretender/config/mock_config.yaml）
```yaml
mocks:
  - url: ^http://www\.baidu\.com/api/rest/v[0-9]$
    method: GET
    response:
      code: 200
      msg: "mocked v1 or v2"
```
- `url`：支持正则表达式，使用Python re.fullmatch 匹配完整url
- `method`：HTTP方法
- `response`：mock返回内容

## 测试示例
```bash
curl -x http://127.0.0.1:8888 http://www.baidu.com/api/rest/v1
# 返回：{"code":0,"msg":"mocked v1 or v2"}

curl -x http://127.0.0.1:8888 http://www.baidu.com/api/rest/v2
# 返回：{"code":0,"msg":"mocked v1 or v2"}

curl -x http://127.0.0.1:8888 http://www.baidu.com/api/rest/v3
# 实际转发到百度
```


## docker 运行
```bash
mkdir mockConfig && docker run -d -p 8888:8888 -v ./mockConfig:/app/config jsonstiananan/pretender-proxy:latest
```

## 服务配置
1. bootRun方式启动的java项目可以指定jvm参数
```bash
    jvmArgs = [...,
               "-Dhttp.proxyHost=localhost",
               "-Dhttp.proxyPort=8888",
    ]
```
---

如需自定义mock规则，编辑`mock_config.yaml`即可。 