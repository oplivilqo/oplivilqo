"""图片生成模块"""
import os
import random
from PIL import Image

BG_CNT = 16  # 背景图片数量

class ImageGenerator:
    """图片生成器"""

    def __init__(self, base_path: str, cache_path: str):
        self.IMG_SETTINGS = {
            # 角色图尺寸限制
            "avatar_width": 800,
            "avatar_height": 700,
        }
        self.base_path = base_path
        self.cache_path = cache_path
        os.makedirs(self.cache_path, exist_ok=True)

    def fit_image(self, img: Image.Image) -> Image.Image:
        """
        调整图像大小以适应尺寸限制
        保持原图比例不变进行缩放
        """
        max_w, max_h = self.IMG_SETTINGS['avatar_width'], self.IMG_SETTINGS['avatar_height']
        w, h = img.size

        # 计算缩放比例，取较小的那个以确保两个维度都不超限
        scale = min(max_w / w, max_h / h)

        new_w = int(w * scale)
        new_h = int(h * scale)

        return img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    def generate_and_save_images(self, character_name: str, emotion_cnt: int,
                                  progress_callback=None) -> None:
        """生成并保存指定角色的所有表情图片"""
        # 检查是否已经生成过
        for filename in os.listdir(self.cache_path):
            if filename.startswith(character_name):
                return

        total_images = BG_CNT * emotion_cnt

        for j in range(emotion_cnt):
            for i in range(BG_CNT):
                background_path = os.path.join(
                    self.base_path, 'assets', "background", f"c{i + 1}.png"
                )
                avatar_path = os.path.join(
                    self.base_path, 'assets', 'chara', character_name,
                    f"{character_name} ({j + 1}).png"
                )

                background = Image.open(background_path).convert("RGBA")
                avatar = self.fit_image(Image.open(avatar_path).convert("RGBA"))

                # avatar左上角坐标：左侧对齐，底端对齐
                target_x = 0  # 左侧对齐
                target_y = background.size[1] - avatar.size[1]  # 底端对齐

                img_num = j * BG_CNT + i + 1
                result = background.copy()
                result.paste(avatar, (target_x, target_y), avatar)

                save_path = os.path.join(
                    self.cache_path, f"{character_name} ({img_num}).jpg"
                )
                result.convert("RGB").save(save_path)

                if progress_callback:
                    progress_callback(j * BG_CNT + i + 1, total_images)

    def get_random_image_name(self, character_name: str, emotion_cnt: int,
                              emote: int | None, value_1: int) -> tuple[str, int]:
        """
        随机获取表情图片名称
        Returns:
            (image_name, new_value_1)
        """
        total_images = BG_CNT * emotion_cnt

        if emote:
            i = random.randint((emote - 1) * BG_CNT + 1, emote * BG_CNT)
            return f"{character_name} ({i})", i

        max_attempts = 100
        attempts = 0
        i = random.randint(1, total_images)

        while attempts < max_attempts:
            i = random.randint(1, total_images)
            current_emotion = (i - 1) // BG_CNT

            if value_1 == -1:
                return f"{character_name} ({i})", i

            if current_emotion != (value_1 - 1) // BG_CNT:
                return f"{character_name} ({i})", i

            attempts += 1

        return f"{character_name} ({i})", i

    def delete_cache(self) -> None:
        """删除缓存文件夹中的所有jpg文件"""
        for filename in os.listdir(self.cache_path):
            if filename.lower().endswith('.jpg'):
                os.remove(os.path.join(self.cache_path, filename))
