import asyncio
import json
import logging
import ssl

import httpx

from src.core.config_manager import ConfigManager
from src.core.cert_manager import CertManager
from src.core.data_generator import DataGenerator

logger = logging.getLogger('Pretender.Proxy')

# 噪音 URL 关键词
_NOISE_PATTERNS = (
    'favicon.ico', 'robots.txt', 'health', 'ping', 'probe',
    'healthcheck', 'status', '.well-known',
)


class AsyncProxyServer:
    """asyncio TCP 代理服务器，同一端口处理 HTTP 和 HTTPS CONNECT"""

    def __init__(self, config_manager: ConfigManager,
                 cert_manager: CertManager,
                 data_generator: DataGenerator,
                 host: str = '0.0.0.0', port: int = 8888):
        self.config_manager = config_manager
        self.cert_manager = cert_manager
        self.data_generator = data_generator
        self.host = host
        self.port = port

    async def start(self):
        server = await asyncio.start_server(self._handle_client, self.host, self.port)
        addr = server.sockets[0].getsockname()
        logger.info(f"代理服务器已启动: {addr[0]}:{addr[1]}")
        async with server:
            await server.serve_forever()

    # ── 连接入口 ─────────────────────────────────────────

    async def _handle_client(self, reader: asyncio.StreamReader,
                             writer: asyncio.StreamWriter):
        try:
            request_line = await self._read_line(reader)
            if not request_line:
                writer.close()
                return

            method, target, _ = self._parse_request_line(request_line)

            if method == 'CONNECT':
                await self._handle_connect(reader, writer, target)
            else:
                await self._handle_http(reader, writer, method, target)
        except (ConnectionResetError, BrokenPipeError):
            pass
        except Exception as e:
            logger.error(f"处理连接异常: {e}")
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    # ── CONNECT (HTTPS MITM) ─────────────────────────────

    async def _handle_connect(self, reader, writer, target):
        host, port = self._parse_host_port(target, default_port=443)

        # 读取并丢弃 CONNECT 的剩余 headers
        await self._read_headers(reader)

        # 告知客户端隧道已建立
        writer.write(b'HTTP/1.1 200 Connection Established\r\n\r\n')
        await writer.drain()

        # TLS 握手——用 CA 签发的域名证书扮演目标服务器
        ssl_ctx = self.cert_manager.get_ssl_context(host)

        transport = writer.transport
        protocol = transport.get_protocol()
        loop = asyncio.get_event_loop()

        # 清除 reader 的 transport 引用，否则 start_tls 内部调用
        # protocol.connection_made() 时 set_transport 会因断言失败
        reader._transport = None

        try:
            tls_transport = await loop.start_tls(
                transport, protocol, ssl_ctx, server_side=True,
            )
        except ssl.SSLError as e:
            logger.warning(f"TLS 握手失败 ({host}): {e}")
            return

        # start_tls 已通过 protocol.connection_made() 将 reader 绑定到新 transport
        # 但 writer 的 transport 引用仍指向旧的，需手动更新
        writer._transport = tls_transport

        # 构造 URL 前缀（非标准端口需包含端口号）
        if port == 443:
            url_prefix = f"https://{host}"
        else:
            url_prefix = f"https://{host}:{port}"

        try:
            # 循环处理同一 TLS 连接上的多个请求（HTTP keep-alive）
            while True:
                req_line = await self._read_line(reader)
                if not req_line:
                    break
                method, path, _ = self._parse_request_line(req_line)
                url = f"{url_prefix}{path}"

                headers = await self._read_headers(reader)
                body = await self._read_body(reader, headers)

                await self._process_request(writer, url, method, headers, body)
        except (ConnectionResetError, BrokenPipeError, ssl.SSLError):
            pass

    # ── 普通 HTTP 代理 ───────────────────────────────────

    async def _handle_http(self, reader, writer, method, url):
        headers = await self._read_headers(reader)
        body = await self._read_body(reader, headers)
        await self._process_request(writer, url, method, headers, body)

    # ── 请求处理核心（HTTP/HTTPS 共用） ───────────────────

    async def _process_request(self, writer, url, method, headers, body):
        # 噪音过滤
        if self._is_noise_request(url):
            logger.debug(f"过滤噪音请求: {method} {url}")
            await self._write_response(writer, 404, {}, b'Not Found')
            return

        logger.info(f"处理请求: {method} {url}")

        # 转换 headers dict 的 key 为 Title-Case
        request_headers = {k.title(): v for k, v in headers.items()}

        # Mock 匹配
        mock_resp = self.config_manager.match_mock(url, method, request_headers)
        if mock_resp is not None:
            if isinstance(mock_resp, dict) and mock_resp.get('error') == 'header_validation_failed':
                logger.warning(f"Header 验证失败: {mock_resp['message']}")
                err = json.dumps(mock_resp, ensure_ascii=False).encode()
                await self._write_response(writer, 401,
                                           {'Content-Type': 'application/json; charset=utf-8'}, err)
            else:
                logger.info(f"Mock 拦截: {method} {url}")
                await self._send_mock_response(writer, mock_resp)
            return

        # 代理转发
        logger.info(f"代理转发: {method} {url}")
        await self._send_proxy_response(writer, url, method, request_headers, body)

    # ── Mock 响应 ─────────────────────────────────────────

    async def _send_mock_response(self, writer, mock_resp):
        if 'delay' in mock_resp:
            delay_s = mock_resp['delay'] / 1000.0
            logger.info(f"模拟延迟: {delay_s:.3f}s")
            await asyncio.sleep(delay_s)

        response_data = self.data_generator.generate_data(mock_resp['msg'])
        body = json.dumps(response_data, ensure_ascii=False).encode('utf-8')
        status = mock_resp.get('code', 200)

        await self._write_response(writer, status,
                                   {'Content-Type': 'application/json; charset=utf-8'}, body)
        logger.info(f"Mock 响应完成: {status}")

    # ── 代理转发 ──────────────────────────────────────────

    async def _send_proxy_response(self, writer, url, method, headers, body):
        proxy_headers = dict(headers)
        proxy_headers.pop('Host', None)
        proxy_headers.pop('Connection', None)
        proxy_headers.pop('Proxy-Connection', None)

        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30,
                                         verify=False) as client:
                resp = await client.request(method=method, url=url,
                                            headers=proxy_headers, content=body or None)

            resp_headers = {}
            hop_by_hop = {
                'connection', 'keep-alive', 'proxy-authenticate',
                'proxy-authorization', 'te', 'trailers', 'upgrade',
                'transfer-encoding',
            }
            for k, v in resp.headers.items():
                if k.lower() not in hop_by_hop:
                    resp_headers[k] = v

            await self._write_response(writer, resp.status_code, resp_headers, resp.content)
            logger.info(f"代理响应完成: {resp.status_code}")

        except httpx.TimeoutException:
            logger.error("代理请求超时")
            await self._write_error(writer, 504, 'Gateway Timeout')
        except httpx.RequestError as e:
            logger.error(f"代理请求失败: {e}")
            await self._write_error(writer, 502, f'Proxy Error: {e}')
        except Exception as e:
            logger.error(f"代理处理异常: {e}")
            await self._write_error(writer, 500, 'Internal Server Error')

    # ── HTTP 解析辅助 ─────────────────────────────────────

    @staticmethod
    def _parse_request_line(line: str):
        """解析请求行 → (method, target, version)"""
        parts = line.split(' ', 2)
        if len(parts) == 3:
            return parts[0], parts[1], parts[2]
        if len(parts) == 2:
            return parts[0], parts[1], 'HTTP/1.1'
        return 'GET', '/', 'HTTP/1.1'

    @staticmethod
    def _parse_host_port(target: str, default_port: int = 80):
        """解析 host:port"""
        if ':' in target:
            host, port_str = target.rsplit(':', 1)
            try:
                return host, int(port_str)
            except ValueError:
                return target, default_port
        return target, default_port

    async def _read_line(self, reader) -> str:
        """读取一行（去掉 CRLF），超时返回空字符串"""
        try:
            data = await asyncio.wait_for(reader.readline(), timeout=30)
            if not data:
                return ''
            return data.decode('latin-1').rstrip('\r\n')
        except (asyncio.TimeoutError, ConnectionResetError):
            return ''

    async def _read_headers(self, reader) -> dict:
        """读取到空行为止的所有 headers"""
        headers = {}
        while True:
            line = await self._read_line(reader)
            if not line:
                break
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
        return headers

    async def _read_body(self, reader, headers: dict) -> bytes:
        """根据 Content-Length 读取 body"""
        length = 0
        for k, v in headers.items():
            if k.lower() == 'content-length':
                try:
                    length = int(v)
                except ValueError:
                    length = 0
                break
        if length > 0:
            return await asyncio.wait_for(reader.readexactly(length), timeout=30)
        return b''

    # ── 响应写入 ──────────────────────────────────────────

    @staticmethod
    def _status_phrase(code: int) -> str:
        phrases = {
            200: 'OK', 201: 'Created', 204: 'No Content',
            301: 'Moved Permanently', 302: 'Found', 304: 'Not Modified',
            400: 'Bad Request', 401: 'Unauthorized', 403: 'Forbidden',
            404: 'Not Found', 405: 'Method Not Allowed',
            500: 'Internal Server Error', 502: 'Bad Gateway',
            503: 'Service Unavailable', 504: 'Gateway Timeout',
        }
        return phrases.get(code, 'Unknown')

    async def _write_response(self, writer, status: int,
                              headers: dict, body: bytes):
        """写入原始 HTTP 响应"""
        lines = [f'HTTP/1.1 {status} {self._status_phrase(status)}\r\n']
        headers.setdefault('Content-Length', str(len(body)))
        headers.setdefault('Connection', 'close')
        for k, v in headers.items():
            lines.append(f'{k}: {v}\r\n')
        lines.append('\r\n')

        writer.write(''.join(lines).encode('latin-1'))
        if body:
            writer.write(body)
        await writer.drain()

    async def _write_error(self, writer, status: int, message: str):
        err = json.dumps({
            'error': True, 'code': status, 'message': message,
            'server': 'Pretender Proxy',
        }, ensure_ascii=False).encode('utf-8')
        await self._write_response(writer, status,
                                   {'Content-Type': 'application/json; charset=utf-8'}, err)

    @staticmethod
    def _is_noise_request(url: str) -> bool:
        url_lower = url.lower()
        return any(p in url_lower for p in _NOISE_PATTERNS)
