"""
统一的API配置管理
"""
import os
from typing import Optional

class APIConfig:
    """API配置管理类"""
    
    def __init__(self):
        # 从环境变量或配置文件加载
        self.api_key = self._get_api_key()
        self.base_url = self._get_base_url()
        self.default_model = self._get_default_model()
        
    def _get_api_key(self) -> Optional[str]:
        """获取API密钥"""
        # 优先从环境变量获取
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            return api_key
            
        # 从配置文件获取
        try:
            from config import API_KEY
            return API_KEY
        except ImportError:
            return None
    
    def _get_base_url(self) -> str:
        """获取API基础URL"""
        # 优先从环境变量获取
        base_url = os.getenv('GEMINI_BASE_URL')
        if base_url:
            return base_url
            
        # 从配置文件获取
        try:
            from config import BASE_URL
            return BASE_URL or "http://154.219.127.219:8002/v1"
        except ImportError:
            return "http://154.219.127.219:8002/v1"
    
    def _get_default_model(self) -> str:
        """获取默认模型"""
        # 优先从环境变量获取
        model = os.getenv('GEMINI_DEFAULT_MODEL')
        if model:
            return model
            
        # 从配置文件获取
        try:
            from config import DEFAULT_MODEL
            return DEFAULT_MODEL or "gemini-2.5-flash"
        except ImportError:
            return "gemini-2.5-flash"
    
    def is_configured(self) -> bool:
        """检查API是否已配置"""
        return bool(self.api_key and self.base_url)
    
    def get_config_dict(self) -> dict:
        """获取配置字典"""
        return {
            'api_key': self.api_key,
            'base_url': self.base_url,
            'default_model': self.default_model
        }

# 全局配置实例
api_config = APIConfig()
