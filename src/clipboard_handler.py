"""剪贴板操作模块"""
import io
import os
import tempfile
import subprocess
import time
from sys import platform
from PIL import Image
import pyperclip
import pyclip
from pynput.keyboard import Key, Controller

PLATFORM = platform.lower()

if PLATFORM.startswith('win'):
    try:
        import win32clipboard
    except ImportError:
        print("[red]请先安装 Windows 运行库: pip install pywin32[/red]")
        raise


class ClipboardHandler:
    """剪贴板处理器"""

    def __init__(self, key_delay: float = 0.1):
        self.key_delay = key_delay
        self.kbd_controller = Controller()

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
                image = Image.open(io.BytesIO(png_bytes))
                with io.BytesIO() as output:
                    image.convert("RGB").save(output, "BMP")
                    bmp_data = output.getvalue()[14:]
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

        cmd_key = Key.cmd if PLATFORM == 'darwin' else Key.ctrl

        self.kbd_controller.press(cmd_key)
        self.kbd_controller.press('a')
        self.kbd_controller.release('a')
        self.kbd_controller.press('x')
        self.kbd_controller.release('x')
        self.kbd_controller.release(cmd_key)

        time.sleep(self.key_delay)
        new_clip = pyperclip.paste()
        return new_clip.strip()

    def try_get_image(self) -> Image.Image | None:
        """尝试从剪贴板获取图像"""
        if PLATFORM == 'darwin':
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
                        bmp_data = data
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
        else:
            # todo: Linux 支持
            return None

    def paste_and_send(self, auto_paste: bool, auto_send: bool) -> None:
        """粘贴并发送图片"""
        if auto_paste:
            self.kbd_controller.press(Key.ctrl if PLATFORM != 'darwin' else Key.cmd)
            self.kbd_controller.press('v')
            self.kbd_controller.release('v')
            self.kbd_controller.release(Key.ctrl if PLATFORM != 'darwin' else Key.cmd)

            time.sleep(0.3)

            if auto_send:
                self.kbd_controller.press(Key.enter)
                self.kbd_controller.release(Key.enter)

