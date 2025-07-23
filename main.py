#!/usr/bin/env python3
"""
Pretender - 本地正向代理&Mock服务主入口sh
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


from src.server.proxy_server import run

def main():
    """主函数"""
    print("Pretender - 本地正向代理&Mock服务")
    print("=" * 50)
    print("功能特性:")
    print("- 支持URL正则匹配mock")
    print("- 支持请求头权限验证")
    print("- 支持动态数据生成")
    print("- 支持接口延迟测试")
    print("- 配置文件热加载")
    print("=" * 50)
    
    try:
        run()
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 