"""
统一配置文件管理器
集中管理所有配置的加载和访问
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class Config:
    """统一配置管理器"""

    def __init__(self):
        # 加载环境变量
        load_dotenv()

        # 配置根目录
        self.config_dir = Path(__file__).parent

        # 缓存加载的配置
        self._configs: Dict[str, Dict[str, Any]] = {}
        self._env_config = {}

        # 加载环境变量配置
        self._load_env_config()

    def _load_env_config(self):
        """加载环境变量配置"""
        self._env_config = {
            'llm': {
                'base_url': os.getenv('LLM_BASE_URL', 'https://api.openai.com/v1'),
                'api_key': os.getenv('LLM_API_KEY'),
                'model_name': os.getenv('LLM_MODEL_NAME', 'gpt-4o-mini'),
            },
            'server': {
                'port': int(os.getenv('PORT', 8000)),
            }
        }

    def _load_yaml_config(self, config_name: str) -> Dict[str, Any]:
        """加载YAML配置文件"""
        if config_name in self._configs:
            return self._configs[config_name]

        config_path = self.config_dir / f"{config_name}.yaml"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
                self._configs[config_name] = config
                return config
        except FileNotFoundError:
            print(f"警告: 配置文件 {config_path} 不存在，使用空配置")
            self._configs[config_name] = {}
            return {}
        except Exception as e:
            print(f"错误: 加载配置文件 {config_path} 失败: {e}")
            self._configs[config_name] = {}
            return {}

    def reload_config(self, config_name: Optional[str] = None):
        """重新加载配置"""
        if config_name:
            self._configs.pop(config_name, None)
        else:
            self._configs.clear()
            self._load_env_config()

    # LLM配置
    @property
    def llm_base_url(self) -> str:
        return self._env_config['llm']['base_url']

    @property
    def llm_api_key(self) -> Optional[str]:
        return self._env_config['llm']['api_key']

    @property
    def llm_model_name(self) -> str:
        return self._env_config['llm']['model_name']

    # 服务器配置
    @property
    def server_port(self) -> int:
        return self._env_config['server']['port']

    # Session配置
    @property
    def session_timeout_minutes(self) -> int:
        session_config = self._load_yaml_config('session')
        return session_config.get('session_timeout_minutes', 20)

    # 游戏配置
    def get_game_config(self, config_name: str) -> Dict[str, Any]:
        """获取游戏配置"""
        return self._load_yaml_config(config_name)

    # 图像识别配置
    def get_image_master_config(self, use_mirror: bool = False) -> Dict[str, Any]:
        """获取图像识别配置"""
        config_name = 'image_master_mirror' if use_mirror else 'image_master'
        return self._load_yaml_config(config_name)

    # 通用配置获取
    def get_config(self, config_name: str) -> Dict[str, Any]:
        """获取任意YAML配置"""
        return self._load_yaml_config(config_name)

    def get_config_value(self, config_name: str, key: str, default=None):
        """获取配置中的特定值"""
        config = self.get_config(config_name)
        return config.get(key, default)

# 全局配置实例
config = Config()

# 便捷函数
def get_llm_config():
    """获取LLM配置"""
    return {
        'base_url': config.llm_base_url,
        'api_key': config.llm_api_key,
        'model_name': config.llm_model_name,
    }

def get_session_config():
    """获取Session配置"""
    return {
        'timeout_minutes': config.session_timeout_minutes,
    }

def get_game_config(config_name: str):
    """获取游戏配置"""
    return config.get_game_config(config_name)

def get_image_master_config(use_mirror: bool = False):
    """获取图像识别配置"""
    return config.get_image_master_config(use_mirror)