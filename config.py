"""配置管理模块"""
import os
import yaml
import json


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, base_path):
        self.base_path = base_path
        self.config_path = os.path.join(base_path, "config")
        
    def load_chara_meta(self):
        """加载角色元数据"""
        with open(os.path.join(self.config_path, "chara_meta.yml"), 'r', encoding="utf-8") as fp:
            config = yaml.safe_load(fp)
            return config["mahoshojo"]
    
    def load_text_configs(self):
        """加载文本配置"""
        with open(os.path.join(self.config_path, "text_configs.yml"), 'r', encoding="utf-8") as fp:
            config = yaml.safe_load(fp)
            return config["text_configs"]
    
    def load_keymap(self, platform):
        """加载快捷键映射"""
        with open(os.path.join(self.config_path, "keymap.yml"), 'r', encoding="utf-8") as fp:
            config = yaml.safe_load(fp)
            return config.get(platform, {})
    
    def load_process_whitelist(self, platform):
        """加载进程白名单"""
        with open(os.path.join(self.config_path, "process_whitelist.yml"), 'r', encoding="utf-8") as fp:
            config = yaml.safe_load(fp)
            return config.get(platform, [])
    
    def load_gui_settings(self):
        """加载GUI设置"""
        keymap_file = os.path.join(self.config_path, "keymap.yml")
        default_settings = {
            "font_family": "Arial",
            "font_size": 12,
            "quick_characters": {}
        }
        
        try:
            if os.path.exists(keymap_file):
                with open(keymap_file, 'r', encoding='utf-8') as f:
                    keymap_data = yaml.safe_load(f)
                    gui_settings = keymap_data.get("gui", {})
                    
                    # 合并设置
                    for key, value in default_settings.items():
                        if key not in gui_settings:
                            gui_settings[key] = value
                    return gui_settings
        except Exception as e:
            print(f"加载GUI设置失败: {e}")
            
        return default_settings
    
    def save_gui_settings(self, settings):
        """保存GUI设置到keymap.yml"""
        try:
            keymap_file = os.path.join(self.config_path, "keymap.yml")
            
            # 读取现有的keymap文件
            if os.path.exists(keymap_file):
                with open(keymap_file, 'r', encoding='utf-8') as f:
                    keymap_data = yaml.safe_load(f) or {}
            else:
                keymap_data = {}
            
            # 更新GUI设置
            keymap_data["gui"] = settings
            
            # 写回文件
            with open(keymap_file, 'w', encoding='utf-8') as f:
                yaml.dump(keymap_data, f, allow_unicode=True, default_flow_style=False)
            
            return True
        except Exception as e:
            print(f"保存GUI设置失败: {e}")
            return False


class AppConfig:
    """应用配置类"""
    
    def __init__(self, base_path):
        self.BOX_RECT = ((728, 355), (2339, 800))  # 文本框区域坐标
        self.KEY_DELAY = 0.1  # 按键延迟
        self.AUTO_PASTE_IMAGE = True
        self.AUTO_SEND_IMAGE = True
        self.BASE_PATH = base_path
        self.ASSETS_PATH = os.path.join(base_path, "assets")