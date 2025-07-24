#!/usr/bin/env python3
"""
Pretender ASGI 应用入口
使用 hypercorn 运行: hypercorn app:app --bind 0.0.0.0:8888
"""

import sys
import os
import json
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import httpx
from src.core.config_manager import ConfigManager
from src.handlers.response_handler import ResponseHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('Pretender')

class PretenderASGI:
    """Pretender ASGI应用类"""
    
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(__file__), 'config/mock_config.yaml')
        self.config_manager = ConfigManager(self.config_path)
        self.response_handler = ResponseHandler()
        
        # 创建默认配置文件（如果不存在）
        self._ensure_config_exists()
        
        logger.info(f"Pretender ASGI应用已初始化")
        logger.info(f"配置文件: {self.config_path}")
        logger.info(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _ensure_config_exists(self):
        """确保配置文件存在"""
        if not os.path.exists(self.config_path):
            config_dir = os.path.dirname(self.config_path)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            default_config = """mocks:
  - url: ^http://www\\.example\\.com/api/test$
    method: GET
    response:
      code: 200
      msg:
        message: "Hello Pretender!"
        timestamp: "{{datetime.now}}"
        server: "Pretender ASGI Server"
"""
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.write(default_config)
            logger.info(f"已创建默认配置文件: {self.config_path}")
    
    async def __call__(self, scope, receive, send):
        """ASGI应用入口点"""
        if scope['type'] == 'http':
            await self.handle_http(scope, receive, send)
        else:
            # 不支持的协议类型
            await self.send_error(send, 400, "Unsupported protocol")
    
    async def handle_http(self, scope, receive, send):
        """处理HTTP请求"""
        try:
            method = scope['method']
            path = scope['path']
            query_string = scope.get('query_string', b'').decode()
            headers = dict(scope.get('headers', []))
            
            # 构建URL
            # 如果path已经是完整URL（代理请求），直接使用
            if path.startswith('http://') or path.startswith('https://'):
                url = path
                if query_string:
                    url += f"?{query_string}"
            else:
                # 否则构建完整URL
                host = headers.get(b'host', b'localhost').decode()
                url = f"http://{host}{path}"
                if query_string:
                    url += f"?{query_string}"
            
            # 过滤噪音请求
            if self._is_noise_request(url):
                logger.debug(f"🚫 过滤噪音请求: {method} {url}")
                await self.send_simple_response(send, 404, "Not Found")
                return
            
            logger.info(f"处理请求: {method} {url}")
            
            # 转换headers格式
            request_headers = {}
            for name, value in headers.items():
                if isinstance(name, bytes):
                    name = name.decode()
                if isinstance(value, bytes):
                    value = value.decode()
                request_headers[name.title()] = value
            
            # 检查Mock规则
            mock_resp = self.config_manager.match_mock(url, method, request_headers)
            if mock_resp is not None:
                logger.info(f"🎯 Mock拦截: {method} {url}")
                await self.handle_mock_response(send, mock_resp)
                return
            
            # 代理转发
            logger.info(f"🔄 代理转发: {method} {url}")
            await self.handle_proxy_request(scope, receive, send, url, method, request_headers)
            
        except Exception as e:
            logger.error(f"处理请求时出错: {e}")
            await self.send_error(send, 500, "Internal Server Error")
    
    def _is_noise_request(self, url):
        """检查是否为噪音请求"""
        noise_patterns = [
            'favicon.ico', 'robots.txt', 'health', 'ping', 'probe',
            'healthcheck', 'status', '.well-known'
        ]
        return any(pattern in url.lower() for pattern in noise_patterns)
    
    async def handle_mock_response(self, send, mock_resp):
        """处理Mock响应"""
        # 检查header验证失败
        if isinstance(mock_resp, dict) and mock_resp.get("error") == "header_validation_failed":
            logger.warning(f"🔐 Header验证失败: {mock_resp['message']}")
            await self.send_error(send, 401, mock_resp["message"])
            return
        
        try:
            
            # 处理延迟
            if 'delay' in mock_resp:
                import asyncio
                delay_seconds = mock_resp['delay'] / 1000.0
                logger.info(f"模拟延迟: {delay_seconds:.3f}秒")
                await asyncio.sleep(delay_seconds)
            
            # 生成响应数据
            response_data = self.response_handler.data_generator.generate_data(mock_resp['msg'])
            response_body = json.dumps(response_data, ensure_ascii=False).encode('utf-8')
            
            status_code = mock_resp.get('code', 200)
            
            await send({
                'type': 'http.response.start',
                'status': status_code,
                'headers': [
                    [b'content-type', b'application/json; charset=utf-8'],
                    [b'content-length', str(len(response_body)).encode()],
                    [b'connection', b'close'],
                ]
            })
            
            await send({
                'type': 'http.response.body',
                'body': response_body
            })
            
            logger.info(f"✅ Mock响应完成: {status_code}")
            
        except Exception as e:
            logger.error(f"生成Mock响应失败: {e}")
            await self.send_error(send, 500, "Mock Response Error")
    
    async def handle_proxy_request(self, scope, receive, send, url, method, headers):
        """处理代理请求"""
        try:
            # 读取请求体
            body = b''
            while True:
                message = await receive()
                if message['type'] == 'http.request':
                    body += message.get('body', b'')
                    if not message.get('more_body', False):
                        break
            
            # 清理代理头
            proxy_headers = dict(headers)
            proxy_headers.pop('Host', None)
            proxy_headers.pop('Connection', None)
            
            # 发送代理请求
            async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=proxy_headers,
                    content=body
                )
            
            # 构造响应头
            response_headers = []
            for name, value in response.headers.items():
                # 跳过hop-by-hop头
                if name.lower() in [
                    'connection', 'keep-alive', 'proxy-authenticate',
                    'proxy-authorization', 'te', 'trailers', 'upgrade',
                    'transfer-encoding'
                ]:
                    continue
                response_headers.append([name.encode(), value.encode()])
            
            response_headers.append([b'connection', b'close'])
            
            await send({
                'type': 'http.response.start',
                'status': response.status_code,
                'headers': response_headers
            })
            
            await send({
                'type': 'http.response.body',
                'body': response.content
            })
            
            logger.info(f"✅ 代理响应完成: {response.status_code}")
            
        except httpx.TimeoutException:
            logger.error(f"⏰ 代理请求超时")
            await self.send_error(send, 504, "Gateway Timeout")
        except httpx.RequestError as e:
            logger.error(f"❌ 代理请求失败: {e}")
            await self.send_error(send, 502, f"Proxy Error: {e}")
        except Exception as e:
            logger.error(f"💥 代理处理异常: {e}")
            await self.send_error(send, 500, "Internal Server Error")
    
    async def send_error(self, send, status_code, message):
        """发送错误响应"""
        error_data = {
            "error": True,
            "code": status_code,
            "message": message,
            "server": "Pretender ASGI"
        }
        
        response_body = json.dumps(error_data, ensure_ascii=False).encode('utf-8')
        
        await send({
            'type': 'http.response.start',
            'status': status_code,
            'headers': [
                [b'content-type', b'application/json; charset=utf-8'],
                [b'content-length', str(len(response_body)).encode()],
                [b'connection', b'close'],
            ]
        })
        
        await send({
            'type': 'http.response.body',
            'body': response_body
        })
    
    async def send_simple_response(self, send, status_code, message):
        """发送简单响应"""
        response_body = message.encode('utf-8')
        
        await send({
            'type': 'http.response.start',
            'status': status_code,
            'headers': [
                [b'content-type', b'text/plain; charset=utf-8'],
                [b'content-length', str(len(response_body)).encode()],
                [b'connection', b'close'],
            ]
        })
        
        await send({
            'type': 'http.response.body',
            'body': response_body
        })

# 创建ASGI应用实例
app = PretenderASGI()

if __name__ == "__main__":
    # 如果直接运行此文件，提示使用hypercorn
    print("🚀 Pretender ASGI应用")
    print("=" * 50)
    print("请使用 hypercorn 运行此应用:")
    print("  hypercorn app:app --bind 0.0.0.0:8888")
    print("  hypercorn app:app --bind 0.0.0.0:8888 --workers 4")
    print("  hypercorn app:app --bind 0.0.0.0:8888 --reload")
    print("=" * 50) 