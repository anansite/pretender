import json
import random
import re
from faker import Faker
from datetime import datetime, timedelta

class DataGenerator:
    def __init__(self):
        self.faker = Faker(['zh_CN', 'en_US'])
        self.faker.seed_instance(42)  # 固定种子，保证可重现
    
    def generate_data(self, template):
        """根据模板生成数据"""
        if isinstance(template, str):
            return self._process_template(template)
        elif isinstance(template, dict):
            return self._process_dict(template)
        elif isinstance(template, list):
            return self._process_list(template)
        else:
            return template
    
    def _process_template(self, template):
        """处理字符串模板"""
        # 支持 {{faker.method:param1,param2}} 和 {{random.method:param1,param2}} 格式
        pattern = r'\{\{(\w+(?:\.\w+)*)(?::([^}]+))?\}\}'
        
        def replace_var(match):
            var_name = match.group(1)
            params_str = match.group(2) if match.group(2) else ""
            
            # 解析参数
            params = []
            if params_str:
                # 处理字符串参数（用引号包围的）
                str_pattern = r'"([^"]*)"'
                str_params = re.findall(str_pattern, params_str)
                # 处理数字参数
                num_pattern = r'\b(\d+(?:\.\d+)?)\b'
                num_params = re.findall(num_pattern, params_str)
                # 处理布尔参数
                bool_pattern = r'\b(true|false)\b'
                bool_params = re.findall(bool_pattern, params_str, re.IGNORECASE)
                
                params = str_params + [float(x) if '.' in x else int(x) for x in num_params] + [x.lower() == 'true' for x in bool_params]
            
            if var_name.startswith('faker.'):
                method_name = var_name[6:]  # 去掉 'faker.'
                try:
                    method = getattr(self.faker, method_name)
                    if params:
                        return str(method(*params))
                    else:
                        # 使用默认参数
                        return self._get_faker_default(method, method_name)
                except (AttributeError, TypeError) as e:
                    return f"{{{{ERROR: {var_name} - {str(e)}}}}}"
            elif var_name.startswith('random.'):
                method_name = var_name[7:]  # 去掉 'random.'
                try:
                    method = getattr(random, method_name)
                    if params:
                        if method_name == 'choice':
                            return str(method(params))
                        elif method_name == 'sample' and len(params) >= 2:
                            return str(method(params[0], params[1]))
                        else:
                            return str(method(*params))
                    else:
                        # 使用默认参数
                        return self._get_random_default(method, method_name)
                except (AttributeError, TypeError) as e:
                    return f"{{{{ERROR: {var_name} - {str(e)}}}}}"
            elif var_name.startswith('datetime.'):
                method_name = var_name[9:]  # 去掉 'datetime.'
                try:
                    method = getattr(datetime, method_name)
                    if method_name in ['now', 'today', 'utcnow']:
                        return str(method())
                    elif params:
                        if method_name == 'strftime':
                            return str(method(*params))
                        elif method_name == 'strptime' and len(params) >= 2:
                            return str(method(*params))
                        elif method_name == 'timedelta':
                            return str(timedelta(*params))
                    else:
                        # 使用默认参数
                        return self._get_datetime_default(method, method_name)
                except (AttributeError, TypeError) as e:
                    return f"{{{{ERROR: {var_name} - {str(e)}}}}}"
            else:
                return f"{{{{UNKNOWN: {var_name}}}}}"
        
        return re.sub(pattern, replace_var, template)
    
    def _get_faker_default(self, method, method_name):
        """获取Faker方法的默认参数"""
        try:
            if method_name == 'random_number':
                return str(method(digits=8))
            elif method_name == 'text':
                return str(method(max_nb_chars=200))
            elif method_name == 'sentence':
                return str(method(nb_words=6))
            elif method_name == 'paragraph':
                return str(method(nb_sentences=3))
            else:
                return str(method())
        except:
            return str(method())
    
    def _get_random_default(self, method, method_name):
        """获取Random方法的默认参数"""
        try:
            if method_name == 'uniform':
                return str(method(0, 1000))
            elif method_name == 'randint':
                return str(method(1, 100))
            elif method_name == 'randrange':
                return str(method(0, 100))
            elif method_name == 'choice':
                return str(method(['option1', 'option2', 'option3']))
            elif method_name == 'sample':
                return str(method(['a', 'b', 'c', 'd', 'e'], 3))
            elif method_name == 'shuffle':
                return f"{{{{ERROR: {method_name} - 不适合在模板中使用}}}}"
            elif method_name == 'gauss':
                return str(method(0, 1))
            elif method_name == 'expovariate':
                return str(method(1.0))
            elif method_name == 'triangular':
                return str(method(0, 1, 0.5))
            else:
                return str(method())
        except:
            return str(method())
    
    def _get_datetime_default(self, method, method_name):
        """获取Datetime方法的默认参数"""
        try:
            if method_name == 'strftime':
                return str(method('%Y-%m-%d %H:%M:%S'))
            elif method_name == 'strptime':
                return f"{{{{ERROR: {method_name} - 需要两个参数}}}}"
            elif method_name == 'timedelta':
                return str(timedelta(days=1))
            else:
                return str(method())
        except:
            return str(method())
    
    def _process_dict(self, data):
        """处理字典类型数据"""
        result = {}
        for key, value in data.items():
            if isinstance(value, str) and ('{{' in value and '}}' in value):
                result[key] = self._process_template(value)
            elif isinstance(value, (dict, list)):
                result[key] = self.generate_data(value)
            else:
                result[key] = value
        return result
    
    def _process_list(self, data):
        """处理列表类型数据"""
        result = []
        for item in data:
            if isinstance(item, str) and ('{{' in item and '}}' in item):
                result.append(self._process_template(item))
            elif isinstance(item, (dict, list)):
                result.append(self.generate_data(item))
            else:
                result.append(item)
        return result
    
    def generate_user_data(self):
        """生成用户数据示例"""
        return {
            "id": self.faker.uuid4(),
            "name": self.faker.name(),
            "email": self.faker.email(),
            "phone": self.faker.phone_number(),
            "address": self.faker.address(),
            "company": self.faker.company(),
            "job": self.faker.job(),
            "created_at": self.faker.date_time_this_year().isoformat(),
            "avatar": self.faker.image_url()
        }
    
    def generate_order_data(self):
        """生成订单数据示例"""
        return {
            "order_id": f"ORD-{self.faker.random_number(digits=8)}",
            "customer_name": self.faker.name(),
            "customer_email": self.faker.email(),
            "items": [
                {
                    "product_id": self.faker.random_number(digits=6),
                    "product_name": self.faker.word().title(),
                    "quantity": random.randint(1, 10),
                    "price": round(random.uniform(10, 1000), 2)
                } for _ in range(random.randint(1, 5))
            ],
            "total_amount": round(random.uniform(100, 5000), 2),
            "status": random.choice(["pending", "processing", "shipped", "delivered"]),
            "created_at": self.faker.date_time_this_year().isoformat(),
            "shipping_address": self.faker.address()
        }
    
    def generate_product_data(self):
        """生成产品数据示例"""
        return {
            "product_id": self.faker.random_number(digits=6),
            "name": self.faker.word().title(),
            "description": self.faker.text(max_nb_chars=200),
            "price": round(random.uniform(10, 1000), 2),
            "category": random.choice(["Electronics", "Clothing", "Books", "Home", "Sports"]),
            "brand": self.faker.company(),
            "stock": random.randint(0, 1000),
            "rating": round(random.uniform(1, 5), 1),
            "reviews_count": random.randint(0, 500),
            "created_at": self.faker.date_time_this_year().isoformat()
        } 