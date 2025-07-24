import yaml
import os
import re
import time
import logging
from datetime import datetime

class ConfigManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self._config_cache = None
        self._config_mtime = None
        self._last_check_time = 0
        self._check_interval = 1.0  # 最小检查间隔1秒，避免频繁文件系统调用
        
        # 设置专用的logger
        self.logger = logging.getLogger('Pretender.Config')
    
    def load_config_if_changed(self):
        """加载配置文件，支持热更新，优化频繁检查"""
        current_time = time.time()
        
        # 如果距离上次检查时间不足指定间隔，直接返回缓存
        if (self._config_cache is not None and 
            current_time - self._last_check_time < self._check_interval):
            return self._config_cache
        
        try:
            # 检查文件是否存在
            if not os.path.exists(self.config_path):
                self.logger.error(f"❌ 配置文件不存在: {self.config_path}")
                return {}
            
            # 获取文件修改时间
            mtime = os.path.getmtime(self.config_path)
            mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            self._last_check_time = current_time
            
            # 检查是否需要重新加载
            if self._config_cache is None:
                # 首次加载
                self.logger.info(f"📋 加载配置文件: {self.config_path} ({mtime_str})")
                self._load_config_from_file()
                self._config_mtime = mtime
                
            elif mtime != self._config_mtime:
                # 修改时间发生变化，需要重新加载
                self.logger.info(f"🔄 配置文件已修改，重新加载: {mtime_str}")
                self._load_config_from_file()
                self._config_mtime = mtime
                
        except Exception as e:
            self.logger.error(f"💥 加载配置文件失败: {e}")
            self._config_cache = {}
            
        return self._config_cache
    
    def _load_config_from_file(self):
        """从文件加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config_cache = yaml.safe_load(f)
            
            # 简单统计
            if self._config_cache:
                mock_count = len(self._config_cache.get('mocks', []))
                self.logger.info(f"✅ 配置加载完成: {mock_count} 个Mock规则")
            else:
                self.logger.warning("⚠️  配置文件为空")
                
        except yaml.YAMLError as e:
            self.logger.error(f"❌ YAML格式错误: {e}")
            self._config_cache = {}
        except Exception as e:
            self.logger.error(f"💥 读取配置文件异常: {e}")
            self._config_cache = {}
    
    def match_headers(self, rule_headers, request_headers):
        """匹配请求头"""
        if not rule_headers:
            return True, None
        
        for header_name, header_pattern in rule_headers.items():
            header_value = request_headers.get(header_name, '')
            if not re.search(header_pattern, header_value):
                error_msg = f"Header validation failed: {header_name}={header_value}, expected pattern: {header_pattern}"
                return False, error_msg
        return True, None
    
    def match_mock(self, url, method, headers):
        """匹配mock规则，包含header验证"""
        config = self.load_config_if_changed()
        for rule in config.get('mocks', []):
            # URL和Method匹配
            pattern = rule['url']
            if not re.fullmatch(pattern, url) or rule['method'].upper() != method.upper():
                continue
            
            # Header验证
            if 'headers' in rule:
                is_valid, error_msg = self.match_headers(rule['headers'], headers)
                if not is_valid:
                    return {"error": "header_validation_failed", "message": error_msg}
            
            return rule['response']
        return None 