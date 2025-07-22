import http.server
import httpx
import os
from ..core.config_manager import ConfigManager
from ..handlers.response_handler import ResponseHandler

class ProxyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.config_manager = ConfigManager(os.path.join(os.path.dirname(__file__), '../../config/mock_config.yaml'))
        self.response_handler = ResponseHandler()
        super().__init__(*args, **kwargs)
    
    def do_METHOD(self):
        url = self.path
        if not url.startswith('http'):
            url = f"http://{self.headers['Host']}{self.path}"
        method = self.command
        
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
            body = self.rfile.read(int(self.headers.get('Content-Length', 0))) if 'Content-Length' in self.headers else None
            
            with httpx.Client(follow_redirects=True) as client:
                resp = client.request(method, url, headers=headers, content=body, timeout=30)
            
            self.response_handler.send_proxy_response(self, resp)
        except Exception as e:
            self.send_error(502, f"Proxy error: {e}")

    def do_GET(self): self.do_METHOD()
    def do_POST(self): self.do_METHOD()
    def do_PUT(self): self.do_METHOD()
    def do_DELETE(self): self.do_METHOD()
    def do_PATCH(self): self.do_METHOD()
    def do_OPTIONS(self): self.do_METHOD()

def run(server_class=http.server.ThreadingHTTPServer, handler_class=ProxyHTTPRequestHandler, port=8888):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Serving HTTP Proxy on port {port} ...")
    httpd.serve_forever()

if __name__ == '__main__':
    run() 