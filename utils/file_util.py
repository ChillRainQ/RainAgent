import base64
import os

import yaml


def read_config(path: str):
    content = read_file(path)
    if content is None:
        return None
    try:
        return yaml.safe_load(content)
    except yaml.YAMLError as e:
        print(e)

def read_file(path: str) -> str | None:
    """
    读取文件内容
    :param path: 文件路径
    :return: 文件内容字符串，失败返回None
    """
    if not os.path.exists(path):
        print(f"[read_file] 文件不存在: {path}")
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"[read_file] 读取失败: {e}")
        return None


def write_file(path: str, content: str, type: int = 0) -> bool:
    """
    写入文件内容
    :param path: 文件路径
    :param content: 写入内容
    :param type: 写入模式 0=覆盖写入 1=追加写入
    :return: 是否成功
    """
    mode = "a" if type == 1 else "w"

    # 自动创建父目录
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)

    try:
        with open(path, mode, encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"[write_file] 写入失败: {e}")
        return False

def _image_to_base64(self, image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")