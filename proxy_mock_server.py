import http.server
import json
import os
import re

import httpx
import yaml

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config/mock_config.yaml')

_config_cache = None
_config_mtime = None

def load_config_if_changed():
    global _config_cache, _config_mtime
    try:
        mtime = os.path.getmtime(CONFIG_PATH)
        if _config_cache is None or mtime != _config_mtime:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                _config_cache = yaml.safe_load(f)
            _config_mtime = mtime
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        _config_cache = {}
    return _config_cache

def match_mock(url, method):
    config = load_config_if_changed()
    for rule in config.get('mocks', []):
        pattern = rule['url']
        if re.fullmatch(pattern, url) and rule['method'].upper() == method.upper():
            return rule['response']
    return None

class ProxyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_METHOD(self):
        url = self.path
        # if not url.startswith('http'):
        #     url = f"http://{self.headers['Host']}{self.path}"
        method = self.command
        mock_resp = match_mock(url, method)
        if mock_resp is not None:
            self.send_response(mock_resp['code'])
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(mock_resp['msg']).encode('utf-8'))
            return

        # 代理转发
        try:
            headers = dict(self.headers)
            headers.pop('Host', None)
            body = self.rfile.read(int(self.headers.get('Content-Length', 0))) if 'Content-Length' in self.headers else None
            with httpx.Client(follow_redirects=True) as client:
                resp = client.request(method, url, headers=headers, content=body, timeout=30)
            self.send_response(resp.status_code)
            for k, v in resp.headers.items():
                if k.lower() == 'transfer-encoding':
                    continue
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(resp.content)
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