"""图片处理模块"""
import os
import random
from PIL import Image
import threading
from typing import Callable, Optional

from text_fit_draw import draw_text_auto
from image_fit_paste import paste_image_auto


class ImageProcessor:
    """图片处理器"""
    
    def __init__(self, base_path: str, box_rect: tuple, text_configs_dict: dict):
        self.base_path = base_path
        self.box_rect = box_rect
        self.text_configs_dict = text_configs_dict
        self.background_count = 16  # 假设有16个背景图片
        
    def generate_precomposed_images(self, character_name: str, emotion_count: int, 
                                  cache_path: str, progress_callback: Optional[Callable] = None) -> None:
        """生成预合成图片"""
        # 检查是否已经生成过
        for filename in os.listdir(cache_path):
            if filename.startswith(character_name):
                return

        total_images = self.background_count * emotion_count

        for j in range(emotion_count):
            for i in range(self.background_count):
                background_path = os.path.join(
                    self.base_path, 'assets', "background", f"c{i + 1}.png"
                )
                overlay_path = os.path.join(
                    self.base_path, 'assets', 'chara', character_name,
                    f"{character_name} ({j + 1}).png"
                )

                background = Image.open(background_path).convert("RGBA")
                overlay = Image.open(overlay_path).convert("RGBA")

                img_num = j * self.background_count + i + 1
                result = background.copy()
                # 使用原始位置 (0, 134)
                result.paste(overlay, (0, 134), overlay)

                save_path = os.path.join(
                    cache_path, f"{character_name} ({img_num}).jpg"
                )
                result.convert("RGB").save(save_path)

                if progress_callback:
                    progress_callback(j * self.background_count + i + 1, total_images)
    
    def generate_image_directly(self, character_name: str, background_index: int, 
                               emotion_index: int, text: str = None, 
                               content_image: Image.Image = None,
                               font_path: str = None) -> bytes:
        """直接生成图片（不预合成模式）"""
        background_path = os.path.join(self.base_path, 'assets', "background", f"c{background_index}.png")
        overlay_path = os.path.join(self.base_path, 'assets', 'chara', character_name, 
                                   f"{character_name} ({emotion_index}).png")

        text_box_topleft = (self.box_rect[0][0], self.box_rect[0][1])
        image_box_bottomright = (self.box_rect[1][0], self.box_rect[1][1])

        if content_image is not None:
            return paste_image_auto(
                image_source=background_path,
                image_overlay=overlay_path,
                top_left=text_box_topleft,
                bottom_right=image_box_bottomright,
                content_image=content_image,
                align="center",
                valign="middle",
                padding=12,
                allow_upscale=True,
                keep_alpha=True,
                role_name=character_name,
                text_configs_dict=self.text_configs_dict,
                base_path=self.base_path,
                overlay_offset=(0, 134)  # 使用原始位置
            )
        elif text is not None and text != "":
            return draw_text_auto(
                image_source=background_path,
                image_overlay=overlay_path,
                top_left=text_box_topleft,
                bottom_right=image_box_bottomright,
                text=text,
                align="left",
                valign='top',
                color=(255, 255, 255),
                max_font_height=145,
                font_path=font_path,
                role_name=character_name,
                text_configs_dict=self.text_configs_dict,
                base_path=self.base_path,
                overlay_offset=(0, 134)  # 使用原始位置
            )
        else:
            raise ValueError("没有文本或图像内容")
    
    def generate_preview_image(self, character_name: str, background_index: int, 
                             emotion_index: int, preview_size: tuple = (400, 300)) -> Image.Image:
        """生成预览图片"""
        try:
            background_path = os.path.join(self.base_path, 'assets', "background", f"c{background_index}.png")
            overlay_path = os.path.join(self.base_path, 'assets', 'chara', character_name, 
                                       f"{character_name} ({emotion_index}).png")

            background = Image.open(background_path).convert("RGBA")
            overlay = Image.open(overlay_path).convert("RGBA")

            # 合成基础图片 - 使用原始位置
            result = background.copy()
            result.paste(overlay, (0, 134), overlay)  # 使用原始位置
            
            # 调整大小用于预览
            result.thumbnail(preview_size, Image.Resampling.LANCZOS)
            
            return result
        except Exception as e:
            print(f"生成预览图片失败: {e}")
            # 返回一个空白图片作为占位符
            return Image.new("RGB", preview_size, color="gray")
    
    def get_random_background(self) -> int:
        """随机选择背景"""
        return random.randint(1, self.background_count)