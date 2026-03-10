#!/usr/bin/env python3
"""
Pretender — 本地正向代理 & Mock 服务
支持 HTTP 和 HTTPS (MITM) 代理

启动: python app.py
"""

import sys
import os
import asyncio
import logging

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.config_manager import ConfigManager
from src.core.cert_manager import CertManager
from src.core.data_generator import DataGenerator
from src.server.async_proxy import AsyncProxyServer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Pretender')
logging.getLogger('asyncio').setLevel(logging.ERROR)


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, 'config/mock_config.yaml')
    certs_dir = os.path.join(base_dir, 'certs')

    host = os.environ.get('PRETENDER_HOST', '0.0.0.0')
    port = int(os.environ.get('PRETENDER_PORT', '8888'))

    # 初始化核心组件
    config_manager = ConfigManager(config_path)
    cert_manager = CertManager(certs_dir)
    data_generator = DataGenerator()

    ca_crt = os.path.join(certs_dir, 'ca.crt')
    logger.info("=" * 60)
    logger.info("Pretender — 本地正向代理 & Mock 服务")
    logger.info(f"  监听地址: {host}:{port}")
    logger.info(f"  配置文件: {config_path}")
    logger.info(f"  CA 证书:  {ca_crt}")
    logger.info("  客户端信任 CA 后即可拦截 HTTPS 请求")
    logger.info("=" * 60)

    server = AsyncProxyServer(config_manager, cert_manager, data_generator,
                              host=host, port=port)
    asyncio.run(server.start())


if __name__ == '__main__':
    main()
