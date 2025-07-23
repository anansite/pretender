import yaml
import os
import re

class ConfigManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self._config_cache = None
        self._config_mtime = None
    
    def load_config_if_changed(self):
        """加载配置文件，支持热更新"""
        try:
            # 检查文件是否存在
            if not os.path.exists(self.config_path):
                print(f"配置文件不存在: {self.config_path}")
                return {}
            
            mtime = os.path.getmtime(self.config_path)
            
            # 只有在以下情况才重新加载：
            # 1. 缓存为空（首次加载）
            # 2. 文件修改时间发生变化
            if self._config_cache is None or mtime != self._config_mtime:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config_cache = yaml.safe_load(f)
                self._config_mtime = mtime
                print(f"配置文件已重新加载: {self.config_path}")
                
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            self._config_cache = {}
        return self._config_cache
    
    def match_headers(self, rule_headers, request_headers):
        """匹配请求头"""
        if not rule_headers:
            return True, None
        
        for header_name, header_pattern in rule_headers.items():
            header_value = request_headers.get(header_name, '')
            if not re.search(header_pattern, header_value):
                error_msg = f"Header validation failed: {header_name}={header_value}, expected pattern: {header_pattern}"
                print(error_msg)
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