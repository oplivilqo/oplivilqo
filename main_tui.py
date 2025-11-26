""" Textual UI 版本"""
import random
import time
from pynput.keyboard import Key, Controller, GlobalHotKeys
import pyperclip
import io
from PIL import Image
import pyclip
from sys import platform
from rich import print
import os
import yaml
import tempfile
import subprocess
import threading
from text_fit_draw import draw_text_auto
from image_fit_paste import paste_image_auto
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, RadioSet, RadioButton, Label, ProgressBar
from textual.binding import Binding
from textual.reactive import reactive

PLATFORM = platform.lower()

if PLATFORM.startswith('win'):
    try:
        import win32clipboard
        import keyboard
    except ImportError:
        print("[red]请先安装 Windows 运行库: pip install pywin32 keyboard[/red]")
        raise


class ManosabaTextBox:
    def __init__(self):
        # 常量定义
        self.BOX_RECT = ((728, 355), (2339, 800))  # 文本框区域坐标
        self.KEY_DELAY = 0.1  # 按键延迟
        self.AUTO_PASTE_IMAGE = True  # 自动粘贴图片
        self.AUTO_SEND_IMAGE = True  # 自动发送图片

        self.kbd_controller = Controller()  # 键盘控制器

        # 初始化路径
        self.BASE_PATH = ""  # 基础路径
        self.CONFIG_PATH = ""  # 配置路径
        self.ASSETS_PATH = ""  # 资源路径
        self.CACHE_PATH = ""  # 缓存路径
        self.setup_paths()

        # 加载配置
        self.mahoshojo = {}  # 角色元数据
        self.text_configs_dict = {}  # 文本配置字典
        self.character_list = []  # 角色列表
        self.keymap = {}    # 快捷键映射
        self.load_configs()

        # 状态变量
        self.emote = None   # 表情索引
        self.value_1 = -1   # 我也不知道这是啥我也不敢动
        self.current_character_index = 3    # 当前角色索引，默认第三个角色（sherri）

    def setup_paths(self):
        """设置文件路径"""
        self.BASE_PATH = os.path.dirname(os.path.abspath(__file__))
        self.CONFIG_PATH = os.path.join(self.BASE_PATH, "config")
        self.ASSETS_PATH = os.path.join(self.BASE_PATH, "assets")
        self.CACHE_PATH = os.path.join(self.ASSETS_PATH, "cache")
        os.makedirs(self.CACHE_PATH, exist_ok=True)

    def load_configs(self):
        """从yaml加载配置文件"""
        with open(os.path.join(self.CONFIG_PATH, "chara_meta.yml"), 'r', encoding="utf-8") as fp:
            config = yaml.safe_load(fp)
            self.mahoshojo = config["mahoshojo"]
            self.character_list = list(self.mahoshojo.keys())

        with open(os.path.join(self.CONFIG_PATH, "text_configs.yml"), 'r', encoding="utf-8") as fp:
            config = yaml.safe_load(fp)
            self.text_configs_dict = config["text_configs"]

        with open(os.path.join(self.CONFIG_PATH, "keymap.yml"), 'r', encoding="utf-8") as fp:
            config = yaml.safe_load(fp)
            self.keymap = config.get(PLATFORM, {})

    def get_character(self, index: str | None = None, full_name: bool = False) -> str:
        """
        获取角色名称
        Args:
            index: 角色索引名（不是序号，如果为None则返回当前角色）
            full_name: 是否返回全名
        Returns:
            角色名称 (str)
        """
        if index is not None:
            return self.mahoshojo[index]['full_name'] if full_name else index
        else:
            chara = self.character_list[self.current_character_index - 1]
            return self.mahoshojo[chara]['full_name'] if full_name else chara

    def switch_character(self, index: int) -> bool:
        """切换到指定索引的角色"""
        if 0 < index <= len(self.character_list):
            self.current_character_index = index
            return True
        return False

    def get_current_font(self) -> str:
        """返回当前角色的字体文件绝对路径"""
        return os.path.join(self.BASE_PATH, 'assets', 'fonts',
                            self.mahoshojo[self.get_character()]["font"])

    def get_current_emotion_count(self) -> int:
        """获取当前角色的表情数量"""
        return self.mahoshojo[self.get_character()]["emotion_count"]

    def delete(self, folder_path: str) -> None:
        """删除指定文件夹中的所有jpg文件"""
        for filename in os.listdir(folder_path):
            if filename.lower().endswith('.jpg'):
                os.remove(os.path.join(folder_path, filename))

    def generate_and_save_images(self, character_name: str, progress_callback=None) -> None:
        """生成并保存指定角色的所有表情图片"""
        emotion_cnt = self.mahoshojo[character_name]["emotion_count"]

        # 检查是否已经生成过
        for filename in os.listdir(self.CACHE_PATH):
            if filename.startswith(character_name):
                return

        total_images = 16 * emotion_cnt

        for j in range(emotion_cnt):
            for i in range(16):
                background_path = os.path.join(
                    self.BASE_PATH, 'assets', "background", f"c{i + 1}.png"
                )
                overlay_path = os.path.join(
                    self.BASE_PATH, 'assets', 'chara', character_name,
                    f"{character_name} ({j + 1}).png"
                )

                background = Image.open(background_path).convert("RGBA")
                overlay = Image.open(overlay_path).convert("RGBA")

                img_num = j * 16 + i + 1
                result = background.copy()
                result.paste(overlay, (0, 134), overlay)

                save_path = os.path.join(
                    self.CACHE_PATH, f"{character_name} ({img_num}).jpg"
                )
                result.convert("RGB").save(save_path)

                if progress_callback:
                    progress_callback(j * 16 + i + 1, total_images)

    def get_random_value(self) -> str:
        """随机获取表情图片名称"""
        character_name = self.get_character()
        emotion_cnt = self.get_current_emotion_count()
        total_images = 16 * emotion_cnt

        if self.emote:
            i = random.randint((self.emote - 1) * 16 + 1, self.emote * 16)
            self.value_1 = i
            self.emote = None
            return f"{character_name} ({i})"

        max_attempts = 100
        attempts = 0
        i = random.randint(1, total_images)

        while attempts < max_attempts:
            i = random.randint(1, total_images)
            current_emotion = (i - 1) // 16

            if self.value_1 == -1:
                self.value_1 = i
                return f"{character_name} ({i})"

            if current_emotion != (self.value_1 - 1) // 16:
                self.value_1 = i
                return f"{character_name} ({i})"

            attempts += 1

        self.value_1 = i
        return f"{character_name} ({i})"

    def copy_png_bytes_to_clipboard(self, png_bytes: bytes) -> None:
        """将PNG字节数据复制到剪贴板"""
        try:
            if PLATFORM == 'darwin':
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    tmp.write(png_bytes)
                    tmp_path = tmp.name

                cmd = f"""osascript -e 'set the clipboard to (read (POSIX file "{tmp_path}") as «class PNGf»)'"""
                result = subprocess.run(cmd, shell=True, capture_output=True)

                os.unlink(tmp_path)

                if result.returncode != 0:
                    print(f"复制图片到剪贴板失败: {result.stderr.decode()}")
            elif PLATFORM.startswith('win'):
                # 打开 PNG 字节为 Image
                image = Image.open(io.BytesIO(png_bytes))
                # 转换成 BMP 字节流（去掉 BMP 文件头的前 14 个字节）
                with io.BytesIO() as output:
                    image.convert("RGB").save(output, "BMP")
                    bmp_data = output.getvalue()[14:]
                # 打开剪贴板并写入 DIB 格式
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, bmp_data)
                win32clipboard.CloseClipboard()
            else:
                # todo: Linux 支持
                pass
        except Exception as e:
            print(f"复制图片到剪贴板失败: {e}")

    def cut_all_and_get_text(self) -> str:
        """模拟全选和剪切操作，返回剪切得到的文本内容"""
        pyperclip.copy("")
        if PLATFORM == 'darwin':
            self.kbd_controller.press(Key.cmd)
            self.kbd_controller.press('a')
            self.kbd_controller.release('a')
            self.kbd_controller.press('x')
            self.kbd_controller.release('x')
            self.kbd_controller.release(Key.cmd)

        elif PLATFORM.startswith('win'):
            keyboard.send("CTRL+A")
            keyboard.send("CTRL+X")

        time.sleep(self.KEY_DELAY)
        new_clip = pyperclip.paste()
        return new_clip.strip()

    def try_get_image(self) -> Image.Image | None:
        """尝试从剪贴板获取图像"""
        if PLATFORM=='darwin':
            try:
                data = pyclip.paste()

                if isinstance(data, bytes) and len(data) > 0:
                    try:
                        text = data.decode('utf-8')
                        if len(text) < 10000:
                            return None
                    except (UnicodeDecodeError, AttributeError):
                        pass

                    try:
                        image = Image.open(io.BytesIO(data))
                        image.load()
                        return image
                    except Exception:
                        return None

            except Exception as e:
                print(f"无法从剪贴板获取图像: {e}")
        elif PLATFORM.startswith('win'):
            try:
                win32clipboard.OpenClipboard()
                if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_DIB):
                    data = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)
                    if data:
                        # 将 DIB 数据转换为字节流，供 Pillow 打开
                        bmp_data = data
                        # DIB 格式缺少 BMP 文件头，需要手动加上
                        # BMP 文件头是 14 字节，包含 "BM" 标识和文件大小信息
                        header = b'BM' + (len(bmp_data) + 14).to_bytes(4, 'little') + b'\x00\x00\x00\x00\x36\x00\x00\x00'
                        image = Image.open(io.BytesIO(header + bmp_data))
                        return image
            except Exception as e:
                print("无法从剪贴板获取图像：", e)
            finally:
                try:
                    win32clipboard.CloseClipboard()
                except:
                    pass
            return None

    def start(self) -> str:
        """生成并发送图片，返回状态消息"""
        character_name = self.get_character()
        address = os.path.join(self.CACHE_PATH, self.get_random_value() + ".jpg")
        baseimage_file = address

        text_box_topleft = (self.BOX_RECT[0][0], self.BOX_RECT[0][1])
        image_box_bottomright = (self.BOX_RECT[1][0], self.BOX_RECT[1][1])
        text = self.cut_all_and_get_text()
        image = self.try_get_image()

        if text == "" and image is None:
            return "错误: 没有文本或图像"

        png_bytes = None

        if image is not None:
            try:
                png_bytes = paste_image_auto(
                    image_source=baseimage_file,
                    image_overlay=None,
                    top_left=text_box_topleft,
                    bottom_right=image_box_bottomright,
                    content_image=image,
                    align="center",
                    valign="middle",
                    padding=12,
                    allow_upscale=True,
                    keep_alpha=True,
                    role_name=character_name,
                    text_configs_dict=self.text_configs_dict,
                )
            except Exception as e:
                return f"生成图像失败: {e}"

        elif text is not None and text != "":
            try:
                png_bytes = draw_text_auto(
                    image_source=baseimage_file,
                    image_overlay=None,
                    top_left=text_box_topleft,
                    bottom_right=image_box_bottomright,
                    text=text,
                    align="left",
                    valign='top',
                    color=(255, 255, 255),
                    max_font_height=145,
                    font_path=self.get_current_font(),
                    role_name=character_name,
                    text_configs_dict=self.text_configs_dict,
                )

            except Exception as e:
                return f"生成图像失败: {e}"

        if png_bytes is None:
            return "生成图像失败！"

        self.copy_png_bytes_to_clipboard(png_bytes)

        if self.AUTO_PASTE_IMAGE:
            self.kbd_controller.press(Key.ctrl if PLATFORM != 'darwin' else Key.cmd)
            self.kbd_controller.press('v')
            self.kbd_controller.release('v')
            self.kbd_controller.release(Key.ctrl if PLATFORM != 'darwin' else Key.cmd)

            time.sleep(0.3)

            if self.AUTO_SEND_IMAGE:
                self.kbd_controller.press(Key.enter)
                self.kbd_controller.release(Key.enter)

        return f"成功生成图片！角色: {character_name}, 表情: {1 + (self.value_1 // 16)}"


class ManosabaTUI(App):
    """魔裁文本框生成器 TUI"""

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "textual.tcss"),
              'r',encoding="utf-8") as f:
        CSS = f.read()

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "keymap.yml"),
        'r',encoding="utf-8") as f:
        keymap = yaml.safe_load(f).get(PLATFORM, {})


    TITLE = "魔裁 文本框生成器"
    theme = "tokyo-night"

    current_character = reactive("sherri")
    current_emotion = reactive(1)
    status_msg = reactive("就绪")

    BINDINGS = [
        Binding(keymap['start_generate'], "generate", "生成图片", priority=True),
        Binding(keymap['delete_cache'], "delete_cache", "清除缓存", priority=True),
        Binding(keymap['quit'], "quit", "退出", priority=True),
        Binding(keymap['pause'], "pause", "暂停", priority=True),
    ]

    def __init__(self):
        super().__init__()
        self.active = True
        self.textbox = ManosabaTextBox()
        self.current_character = self.textbox.get_character()
        self.hotkey_listener = None
        self.setup_global_hotkeys()

    def setup_global_hotkeys(self) -> None:
        """设置全局热键监听器"""
        keymap = self.keymap
        if PLATFORM == "darwin":
            hotkeys = {
                keymap['start_generate']: self.trigger_generate
            }

            self.hotkey_listener = GlobalHotKeys(hotkeys)
            self.hotkey_listener.start()
        elif PLATFORM.startswith('win'):
            keyboard.add_hotkey(keymap['start_generate'], self.trigger_generate)



    def trigger_generate(self) -> None:
        """全局热键触发生成图片（在后台线程中调用）"""
        # 使用 call_from_thread 在主线程中安全地调用 action_generate
        if self.active:
            self.call_from_thread(self.action_generate)

    def compose(self) -> ComposeResult:
        """创建UI布局"""
        yield Header()

        with Container(id="main_container"):
            with Horizontal():
                with Vertical(id="character_panel"):
                    yield Label("选择角色 (Character)", classes="panel_title")
                    with ScrollableContainer():
                        with RadioSet(id="character_radio"):
                            for char_id in self.textbox.character_list:
                                char_name = self.textbox.get_character(char_id, full_name=True)
                                yield RadioButton(
                                    f"{char_name} ({char_id})",
                                    value=char_id == self.current_character,
                                    id=f"char_{char_id}"
                                )

                with Vertical(id="emotion_panel"):
                    yield Label("选择表情 (Emotion)", classes="panel_title")
                    with ScrollableContainer():
                        with RadioSet(id="emotion_radio"):
                            emotion_cnt = self.textbox.get_current_emotion_count()
                            for i in range(1, emotion_cnt + 1):
                                yield RadioButton(
                                    f"表情 {i}",
                                    value=(i == 1),
                                    id=f"emotion_{i}"
                                )

            with Horizontal(id="control_panel"):
                yield Label(self.status_msg, id="status_label")
                yield ProgressBar(id="progress_bar")

        yield Footer()

    def on_mount(self) -> None:
        """应用启动时执行"""
        self.update_status(f"当前角色: {self.textbox.get_character(self.current_character, full_name=True)} ")

        # 预加载当前角色（在后台线程中执行）
        char_name = self.textbox.get_character(self.current_character)
        self.load_character_images(char_name)

    def load_character_images(self, char_name: str) -> None:
        """在后台线程中加载角色图片"""

        def load_in_thread():
            def update_progress(current: int, total: int):
                self.call_from_thread(self._update_progress, current, total)

            # 禁用选择框
            self.call_from_thread(self._disable_radio_sets)

            self.call_from_thread(self._show_progress_bar)
            self.call_from_thread(self.update_status,
                                  f"正在加载角色 {self.textbox.get_character(self.current_character, full_name=True)} ...")

            self.textbox.generate_and_save_images(char_name, update_progress)

            self.call_from_thread(self._hide_progress_bar)
            self.call_from_thread(self.update_status,
                                  f"角色 {self.textbox.get_character(self.current_character, full_name=True)} 加载完成 ✓")

            # 恢复选择框
            self.call_from_thread(self._enable_radio_sets)

        thread = threading.Thread(target=load_in_thread, daemon=True)
        thread.start()

    def _show_progress_bar(self) -> None:
        """显示进度条"""
        progress_bar = self.query_one("#progress_bar", ProgressBar)
        progress_bar.add_class("visible")
        progress_bar.update(total=100, progress=0)

    def _hide_progress_bar(self) -> None:
        """隐藏进度条"""
        progress_bar = self.query_one("#progress_bar", ProgressBar)
        progress_bar.remove_class("visible")

    def _update_progress(self, current: int, total: int) -> None:
        """更新进度条"""
        progress_bar = self.query_one("#progress_bar", ProgressBar)
        progress_bar.update(total=total, progress=current)

    def _disable_radio_sets(self) -> None:
        """禁用所有RadioSet"""
        try:
            char_radio = self.query_one("#character_radio", RadioSet)
            char_radio.disabled = True

            emotion_radio = self.query_one("#emotion_radio", RadioSet)
            emotion_radio.disabled = True
        except Exception as e:
            self.notify(str(e), title="禁用选择框失败", severity="warning")

    def _enable_radio_sets(self) -> None:
        """启用所有RadioSet"""
        try:
            char_radio = self.query_one("#character_radio", RadioSet)
            char_radio.disabled = False

            emotion_radio = self.query_one("#emotion_radio", RadioSet)
            emotion_radio.disabled = False
        except Exception as e:
            self.notify(str(e), title="启用选择框失败", severity="warning")

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """当RadioSet选项改变时"""
        if event.radio_set.id == "character_radio":
            selected_char = event.pressed.id.replace("char_", "")
            self.current_character = selected_char

            # 更新角色索引
            char_idx = self.textbox.character_list.index(selected_char) + 1
            self.textbox.switch_character(char_idx)

            # 预加载新角色（使用带进度条的加载方法）
            self.load_character_images(selected_char)

            # 重新生成表情选项（延迟执行以确保状态更新完成）
            self.call_after_refresh(self.refresh_emotion_panel)

        elif event.radio_set.id == "emotion_radio":
            # 从按钮标签中提取表情编号
            try:
                label = event.pressed.label.plain
                emotion_num = int(label.split()[-1])
                self.current_emotion = emotion_num
                self.textbox.emote = emotion_num
                self.update_status(f"已选择表情 {emotion_num} 喵")
            except (ValueError, AttributeError, IndexError) as e:
                self.update_status(e)
                pass

    def refresh_emotion_panel(self) -> None:
        """刷新表情面板"""
        emotion_radio = self.query_one("#emotion_radio", RadioSet)

        # 获取所有子组件并逐个移除
        children = list(emotion_radio.children)
        for child in children:
            try:
                child.remove()
            except Exception:
                pass

        # 重置表情为 1
        self.current_emotion = 1
        self.textbox.emote = 1

        # 添加新的按钮
        emotion_cnt = self.textbox.get_current_emotion_count()
        for i in range(1, emotion_cnt + 1):
            unique_id = f"emotion_{self.current_character}_{i}"
            btn = RadioButton(
                f"表情 {i}",
                value=(self.textbox.emote == i),
                id=unique_id
            )
            emotion_radio.mount(btn)

    def update_status(self, msg: str) -> None:
        """更新状态栏"""
        self.status_msg = msg
        status_label = self.query_one("#status_label", Label)
        status_label.update(msg)

    def action_pause(self):
        """切换暂停状态"""
        self.active = not self.active
        status = "激活" if self.active else "暂停"
        self.update_status(f"应用已{status}。")
        main_container = self.query_one("#main_container")
        main_container.disabled = not self.active


    def action_generate(self) -> None:
        """生成图片"""
        self.update_status("正在生成图片...")
        result = self.textbox.start()
        self.update_status(result)

    def action_delete_cache(self) -> None:
        """清除缓存"""
        self.update_status("正在清除缓存...")
        self.textbox.delete(self.textbox.CACHE_PATH)
        self.update_status("缓存已清除，需要重新加载角色")

    def action_quit(self) -> None:
        """退出应用"""
        # 停止全局热键监听器
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        self.exit()


if __name__ == "__main__":
    app = ManosabaTUI()
    app.run()
