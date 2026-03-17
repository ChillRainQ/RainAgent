import os
import os.path
import base64
import shutil

from agent_tools import register
from agent_tools.register import BaseTool
from utils import file_util, xml_util


def _capture(**_) -> str:
    """截取全屏，返回 base64"""
    import mss
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # 1=主屏幕
        img = sct.grab(monitor)
        png = mss.tools.to_png(img.rgb, img.size)
    return base64.b64encode(png).decode("utf-8")


@register.register
class FileTool(BaseTool):
    name = "file"
    desc = "文件操作工具"

    def invoke(self, **kwargs) -> str:
        res, err = self.permission_check(kwargs)
        if not res:
            return err
        action = kwargs.pop(xml_util.INVOKE_TAG, None)
        if action is None:
            return f"{self.err}: 缺少 {xml_util.INVOKE_TAG} 参数"
        actions = {
            "read": self._read,
            "write": self._write,
            "delete": self._delete,
            "exists": self._exists,
            "isdir": self._isdir,
            "ls": self._ls,
            "read_image": self._read_image,
            "copy": self._copy,  # ← 新增
            "copy_image": self._copy_image,
            "capture": _capture,
            "capture_region": self._capture_region,
        }
        func = actions.get(action)
        if func is None:
            return f"{self.err}: 不支持的操作: {action}"
        try:
            return func(**kwargs)
        except Exception as e:
            return f"{self.err}: {e}"

    def _read(self, path: str) -> str:
        return file_util.read_file(path) or f"{self.err}: 文件不存在"

    def _write(self, path: str, content: str, type: int = 0) -> str:
        return "成功" if file_util.write_file(path, content, type) else "失败"

    def _delete(self, path: str) -> str:
        if os.path.exists(path):
            os.remove(path)
            return "删除成功"
        return f"{self.err}: 文件不存在"

    def _exists(self, path: str) -> str:
        return str(os.path.exists(path))

    def _isdir(self, path: str) -> str:
        return str(os.path.isdir(path))

    def _ls(self, path: str) -> str:
        if not os.path.exists(path):
            return f"{self.err}: 路径不存在"
        if not os.path.isdir(path):
            return f"{self.err}: 不是目录"
        items = os.listdir(path)
        if not items:
            return "（空目录）"
        result = []
        for item in items:
            full = os.path.join(path, item)
            tag = "[目录]" if os.path.isdir(full) else "[文件]"
            result.append(f"{tag} {item}")
        return "\n".join(result)

    def _read_image(self, path: str) -> str:
        if not os.path.exists(path):
            return f"{self.err}: 文件不存在"
        ext = os.path.splitext(path)[-1].lower()
        supported = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"]
        if ext not in supported:
            return f"{self.err}: 不支持的图片格式: {ext}，支持: {', '.join(supported)}"
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _copy(self, src: str, dst: str) -> str:
        """复制文本文件"""
        if not os.path.exists(src):
            return f"{self.err}: 源文件不存在"
        if os.path.isdir(src):
            return f"{self.err}: 源路径是目录，请使用 copy_dir"
        dst_dir = os.path.dirname(dst)
        if dst_dir:
            os.makedirs(dst_dir, exist_ok=True)
        shutil.copy2(src, dst)  # copy2 会保留元数据
        return "复制成功"

    def _copy_image(self, src: str, dst: str) -> str:
        """复制二进制文件（图片等），本质上和 copy 一样，语义上更明确"""
        return self._copy(src, dst)

    def _capture_region(self, x: str, y: str, width: str, height: str, **_) -> str:
        """截取指定区域"""
        import mss
        region = {
            "left": int(x),
            "top": int(y),
            "width": int(width),
            "height": int(height),
        }
        with mss.mss() as sct:
            img = sct.grab(region)
            png = mss.tools.to_png(img.rgb, img.size)
        return base64.b64encode(png).decode("utf-8")

    def to_prompt(self) -> str:
        return (
            "- file: 文件操作工具\n"
            "  支持操作:\n"
            "    read(path: str)\n"
            "    write(path: str, content: str, type: int)\n"
            "      type: 写入模式，0=覆盖写入（默认），1=追加写入\n"
            "    delete(path: str)\n"
            "    exists(path: str)\n"
            "    isdir(path: str)\n"
            "    ls(path: str)\n"
            "    read_image(path: str)\n"
            "    copy(src: str, dst: str)        # 复制文件（文本或二进制）\n"
            "    copy_image(src: str, dst: str)  # 复制图片等二进制文件\n"
            "    capture()                             截取全屏\n"
            "    capture_region(x, y, width, height)   截取指定区域\n"
            "\n"
            "示例:\n"
            "<file><invoke>read</invoke><path>D:/AgentSpace/test.txt</path></file>\n"
            "<file><invoke>capture</invoke></file>\n"
            "<file><invoke>copy</invoke><src>D:/AgentSpace/a.txt</src><dst>D:/AgentSpace/b.txt</dst></file>\n"
        )