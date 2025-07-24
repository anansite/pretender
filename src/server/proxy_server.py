import http.server
import httpx
import os
import signal
import sys
from ..core.config_manager import ConfigManager
from ..handlers.response_handler import ResponseHandler

class ProxyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    # 类变量，所有实例共享
    config_manager = None
    response_handler = None
    
    def __init__(self, *args, **kwargs):
        # 只在第一次初始化时创建实例
        if ProxyHTTPRequestHandler.config_manager is None:
            config_path = os.path.join(os.path.dirname(__file__), '../../config/mock_config.yaml')
            ProxyHTTPRequestHandler.config_manager = ConfigManager(config_path)
            ProxyHTTPRequestHandler.response_handler = ResponseHandler()
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """重写日志方法，减少无用日志输出"""
        # 过滤一些常见的健康检查和无用请求
        request_line = args[0] if args else ""
        if any(noise in str(request_line).lower() for noise in [
            'favicon.ico', 'robots.txt', 'health', 'ping', 'probe'
        ]):
            return  # 不输出这些请求的日志
        super().log_message(format, *args)
    
    def do_METHOD(self):
        try:
            url = self.path
            if not url.startswith('http'):
                host = self.headers.get('Host', 'localhost')
                if not host:
                    self.send_error(400, "Bad Request: No Host header")
                    return
                url = f"http://{host}{self.path}"
            method = self.command
            
            # 过滤无效请求
            if not url or method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']:
                self.send_error(405, "Method Not Allowed")
                return
            
            # 检查是否需要mock，传入headers进行验证
            mock_resp = self.config_manager.match_mock(url, method, dict(self.headers))
            if mock_resp is not None:
                # 检查是否是header验证失败
                if isinstance(mock_resp, dict) and mock_resp.get("error") == "header_validation_failed":
                    self.response_handler.send_unauthorized_response(self, mock_resp["message"])
                    return
                # 正常mock响应
                self.response_handler.send_mock_response(self, mock_resp)
                return

            # 代理转发
            try:
                headers = dict(self.headers)
                headers.pop('Host', None)
                content_length = int(self.headers.get('Content-Length', 0))
                body = None
                if content_length > 0:
                    if content_length > 10 * 1024 * 1024:  # 限制请求体大小为10MB
                        self.send_error(413, "Payload Too Large")
                        return
                    body = self.rfile.read(content_length)
                
                with httpx.Client(follow_redirects=True, timeout=30) as client:
                    resp = client.request(method, url, headers=headers, content=body)
                
                self.response_handler.send_proxy_response(self, resp)
            except httpx.TimeoutException:
                self.send_error(504, "Gateway Timeout")
            except httpx.RequestError as e:
                self.send_error(502, f"Proxy error: {e}")
            except Exception as e:
                print(f"Unexpected error in proxy: {e}")
                self.send_error(500, "Internal Server Error")
        except Exception as e:
            print(f"Error in do_METHOD: {e}")
            try:
                self.send_error(500, "Internal Server Error")
            except:
                pass  # 连接可能已经关闭

    def do_GET(self): self.do_METHOD()
    def do_POST(self): self.do_METHOD()
    def do_PUT(self): self.do_METHOD()
    def do_DELETE(self): self.do_METHOD()
    def do_PATCH(self): self.do_METHOD()
    def do_OPTIONS(self): self.do_METHOD()
    def do_HEAD(self): self.do_METHOD()

class OptimizedThreadingHTTPServer(http.server.ThreadingHTTPServer):
    """优化的线程HTTP服务器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置socket选项以优化性能
        self.socket.setsockopt(http.server.socket.SOL_SOCKET, http.server.socket.SO_REUSEADDR, 1)
        # 减少TIME_WAIT状态的socket数量
        if hasattr(http.server.socket, 'SO_REUSEPORT'):
            self.socket.setsockopt(http.server.socket.SOL_SOCKET, http.server.socket.SO_REUSEPORT, 1)
    
    def server_bind(self):
        """绑定服务器地址"""
        super().server_bind()
        self.server_name = self.server_address[0]
        self.server_port = self.server_address[1]

def signal_handler(signum, frame):
    """信号处理器，用于优雅关闭"""
    print("\n正在关闭服务器...")
    if hasattr(signal_handler, 'response_handler'):
        signal_handler.response_handler.shutdown()
    sys.exit(0)

def run(server_class=OptimizedThreadingHTTPServer, handler_class=ProxyHTTPRequestHandler, port=8888):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    
    # 设置信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # 保存response_handler引用以便关闭时清理
    if handler_class.response_handler:
        signal_handler.response_handler = handler_class.response_handler
    
    print(f"Serving HTTP Proxy on port {port} ...")
    print("Press Ctrl+C to stop the server")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n正在关闭服务器...")
        if handler_class.response_handler:
            handler_class.response_handler.shutdown()
    finally:
        httpd.server_close()

if __name__ == '__main__':
    run() 