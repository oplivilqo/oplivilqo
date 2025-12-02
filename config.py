"""配置管理模块"""
import os
from sys import platform
import yaml
from path_utils import get_base_path, get_resource_path, ensure_path_exists


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, base_path=None):
        # 如果没有提供base_path，使用自动检测的路径
        self.base_path = base_path if base_path else get_base_path()
        self.config_path = get_resource_path("config")
        self.ai_config = AIConfig()

        # 规范化平台键
        if platform.startswith('win'):
            self.platform_key = 'win32'
        elif platform == 'darwin':
            self.platform_key = 'darwin'
        else:
            self.platform_key = 'win32'
        
    def load_chara_meta(self):
        """加载角色元数据"""
        chara_meta_path = get_resource_path(os.path.join("config", "chara_meta.yml"))
        with open(chara_meta_path, 'r', encoding="utf-8") as fp:
            config = yaml.safe_load(fp)
            return config["mahoshojo"]
    
    def load_text_configs(self):
        """加载文本配置"""
        text_configs_path = get_resource_path(os.path.join("config", "text_configs.yml"))
        with open(text_configs_path, 'r', encoding="utf-8") as fp:
            config = yaml.safe_load(fp)
            return config["text_configs"]
    
    def load_keymap(self, platform):
        """加载快捷键映射 - 确保文件存在时不会重写"""
        keymap_file = get_resource_path(os.path.join("config", "keymap.yml"))
        
        # 如果文件不存在，创建默认配置
        if not os.path.exists(keymap_file):
            default_keymap = self._get_default_keymap()
            self._save_keymap(default_keymap)
            return default_keymap.get(platform, {})
        
        try:
            with open(keymap_file, 'r', encoding="utf-8") as fp:
                config = yaml.safe_load(fp) or {}
                return config.get(platform, {})
        except Exception as e:
            print(f"加载keymap.yml失败: {e}")
            # 返回默认配置
            return self._get_default_keymap().get(platform, {})
    
    def _get_default_keymap(self):
        """获取默认快捷键配置"""
        return {
            "win32": {
                "start_generate": "ctrl+e",
                "next_character": "ctrl+alt+l",
                "prev_character": "ctrl+alt+j",
                "next_emotion": "ctrl+alt+o",
                "prev_emotion": "ctrl+alt+u",
                "next_background": "ctrl+alt+k",
                "prev_background": "ctrl+alt+i",
                "toggle_listener": "alt+ctrl+p",
                "character_1": "ctrl+1",
                "character_2": "ctrl+2",
                "character_3": "ctrl+3",
                "character_4": "ctrl+4",
                "character_5": "ctrl+5",
                "character_6": "ctrl+6"
            },
            "darwin": {
                "start_generate": "cmd+e",
                "next_character": "cmd+alt+l",
                "prev_character": "cmd+alt+j",
                "next_emotion": "cmd+alt+o",
                "prev_emotion": "cmd+alt+u",
                "next_background": "cmd+alt+k",
                "prev_background": "cmd+alt+i",
                "toggle_listener": "alt+cmd+p",
                "character_1": "cmd+1",
                "character_2": "cmd+2",
                "character_3": "cmd+3",
                "character_4": "cmd+4",
                "character_5": "cmd+5",
                "character_6": "cmd+6"
            }
        }
    
    def _save_keymap(self, keymap_data):
        """保存快捷键配置"""
        try:
            keymap_file = ensure_path_exists(get_resource_path(os.path.join("config", "keymap.yml")))
            # 确保配置目录存在
            os.makedirs(os.path.dirname(keymap_file), exist_ok=True)
            with open(keymap_file, 'w', encoding='utf-8') as f:
                yaml.dump(keymap_data, f, allow_unicode=True, default_flow_style=False)
            return True
        except Exception as e:
            print(f"保存keymap.yml失败: {e}")
            return False
    
    def load_process_whitelist(self):
        """加载进程白名单"""
 
        whitelist_file = get_resource_path(os.path.join("config", "process_whitelist.yml"))
        
        # 如果文件不存在，返回空列表
        if not os.path.exists(whitelist_file):
            return []
            
        try:
            with open(whitelist_file, 'r', encoding="utf-8") as fp:
                config = yaml.safe_load(fp) or {}
                return config.get(self.platform_key, [])
        except Exception as e:
            print(f"加载process_whitelist.yml失败: {e}")
            return []
    
    def save_process_whitelist(self, processes):
        """保存进程白名单"""
        try:
            whitelist_file = ensure_path_exists(get_resource_path(os.path.join("config", "process_whitelist.yml")))
            
            # 如果文件已存在，则先加载现有配置，然后合并
            existing_data = {}
            if os.path.exists(whitelist_file):
                try:
                    with open(whitelist_file, 'r', encoding='utf-8') as f:
                        existing_data = yaml.safe_load(f) or {}
                except Exception as e:
                    print(f"读取现有白名单配置失败: {e}")
            
            # 更新当前平台的白名单
            existing_data[self.platform_key] = processes
            
            # 确保配置目录存在
            os.makedirs(os.path.dirname(whitelist_file), exist_ok=True)
            
            # 保存回文件
            with open(whitelist_file, 'w', encoding='utf-8') as f:
                yaml.dump(existing_data, f, allow_unicode=True, default_flow_style=False)
            
            return True
        except Exception as e:
            print(f"保存进程白名单失败: {e}")
            return False
        
    def load_gui_settings(self):
        """加载GUI设置"""
        settings_file = get_resource_path(os.path.join("config", "settings.yml"))
        default_settings = {
            "font_family": "font3",
            "font_size": 110,
            "quick_characters": {},
            "sentiment_matching": {
                "enabled": False
            },
            "image_compression": {
                "pixel_reduction_enabled": True,
                "pixel_reduction_ratio": 50
            }
        }
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings_data = yaml.safe_load(f) or {}
                    
                    # 合并设置，确保新字段有默认值
                    merged_settings = default_settings.copy()
                    merged_settings.update(settings_data)
                    
                    # 确保各个部分完整
                    if "sentiment_matching" in settings_data:
                        merged_settings["sentiment_matching"].update(settings_data["sentiment_matching"])
                    if "image_compression" in settings_data:
                        merged_settings["image_compression"].update(settings_data["image_compression"])
                    
                    return merged_settings
        except Exception as e:
            print(f"加载GUI设置失败: {e}")
            
        return default_settings
    
    def save_gui_settings(self, settings):
        """保存GUI设置到settings.yml"""
        try:
            settings_file = ensure_path_exists(get_resource_path(os.path.join("config", "settings.yml")))
            
            # 如果文件已存在，则先加载现有配置，然后合并
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    existing_settings = yaml.safe_load(f) or {}
                # 合并设置，新的设置覆盖旧的
                merged_settings = existing_settings.copy()
                merged_settings.update(settings)
            else:
                merged_settings = settings
            
            # 确保配置目录存在
            os.makedirs(os.path.dirname(settings_file), exist_ok=True)
            
            # 写回文件
            with open(settings_file, 'w', encoding='utf-8') as f:
                yaml.dump(merged_settings, f, allow_unicode=True, default_flow_style=False)
            
            return True
        except Exception as e:
            print(f"保存GUI设置失败: {e}")
            return False

class AIConfig:
    """AI配置类"""
    def __init__(self):
        self.ollama = {
            "base_url": "http://localhost:11434/v1/",
            "api_key": "",
            "model": "qwen2.5"
        }
        self.deepseek = {
            "base_url": "https://api.deepseek.com",
            "api_key": "",
            "model": "deepseek-chat"
        }

class AppConfig:
    """应用配置类"""
    
    def __init__(self, base_path=None):
        self.BOX_RECT = ((728, 355), (2339, 800))  # 文本框区域坐标
        self.KEY_DELAY = 0.1  # 按键延迟
        self.AUTO_PASTE_IMAGE = True
        self.AUTO_SEND_IMAGE = True
        # 使用自动检测的基础路径
        self.BASE_PATH = base_path if base_path else get_base_path()
        self.ASSETS_PATH = get_resource_path("assets")