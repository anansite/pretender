import json
import threading
import time
from ..core.data_generator import DataGenerator

class ResponseHandler:
    def __init__(self):
        self.data_generator = DataGenerator()
    
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
            
            # 异步延迟处理
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
            
            # 在后台线程中执行延迟响应
            thread = threading.Thread(target=delayed_response)
            thread.daemon = True
            thread.start()
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