import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from ..core.data_generator import DataGenerator

class ResponseHandler:
    def __init__(self):
        self.data_generator = DataGenerator()
        # 使用线程池管理延迟响应，限制最大线程数
        self._thread_pool = ThreadPoolExecutor(max_workers=10, thread_name_prefix="DelayResponse")
    
    def send_unauthorized_response(self, handler, message="Header validation failed"):
        """发送未授权响应"""
        body = json.dumps({
            "error": "unauthorized",
            "message": message,
            "code": 401
        }, ensure_ascii=False).encode('utf-8')
        handler.send_response(401)
        handler.send_header('Content-Type', 'application/json')
        handler.send_header('Content-Length', str(len(body)))
        handler.send_header('Connection', 'close')
        handler.end_headers()
        handler.wfile.write(body)
        print(f"Unauthorized response sent: {message}")

    def send_mock_response(self, handler, mock_resp):
        """发送mock响应"""
        # 检查是否需要模拟延迟
        if 'delay' in mock_resp:
            delay_seconds = mock_resp['delay'] / 1000.0  # 转换为秒，保持毫秒精度
            print(f"Simulating delay for {mock_resp['delay']}ms ({delay_seconds:.3f}s)...")
            
            # 使用线程池处理延迟响应
            def delayed_response():
                time.sleep(delay_seconds)  # time.sleep支持浮点数，可以实现毫秒级精度
                try:
                    # 生成动态数据
                    response_data = self.data_generator.generate_data(mock_resp['msg'])
                    body = json.dumps(response_data, ensure_ascii=False).encode('utf-8')
                    handler.send_response(mock_resp['code'])
                    handler.send_header('Content-Type', 'application/json')
                    handler.send_header('Content-Length', str(len(body)))
                    handler.send_header('Connection', 'close')
                    handler.end_headers()
                    handler.wfile.write(body)
                    print(f"Delayed response sent with status {mock_resp['code']}")
                except Exception as e:
                    print(f"Error sending delayed response: {e}")
            
            # 使用线程池执行延迟响应，避免无限制创建线程
            self._thread_pool.submit(delayed_response)
            return
        
        # 生成动态数据
        response_data = self.data_generator.generate_data(mock_resp['msg'])
        body = json.dumps(response_data, ensure_ascii=False).encode('utf-8')
        handler.send_response(mock_resp['code'])
        handler.send_header('Content-Type', 'application/json')
        handler.send_header('Content-Length', str(len(body)))
        handler.send_header('Connection', 'close')
        handler.end_headers()
        handler.wfile.write(body)
        print(f"Mocked response with status {mock_resp['code']}")

    def send_proxy_response(self, handler, resp):
        """发送代理转发响应"""
        handler.send_response(resp.status_code)
        for k, v in resp.headers.items():
            # 跳过 hop-by-hop 头部和 Transfer-Encoding
            if k.lower() in [
                'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
                'te', 'trailers', 'upgrade', 'transfer-encoding'
            ]:
                continue
            handler.send_header(k, v)
        handler.send_header('Connection', 'close')
        handler.end_headers()
        handler.wfile.write(resp.content)
        print(f"Proxied response with status {resp.status_code}")
    
    def shutdown(self):
        """关闭线程池"""
        self._thread_pool.shutdown(wait=True) 