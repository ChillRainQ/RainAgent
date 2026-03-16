import os
import os.path
import base64

from agent_tools import register
from agent_tools.register import BaseTool
from utils import file_util


@register.register
class FileTool(BaseTool):
    name = "file"
    desc = "文件操作工具"

    def invoke(self, **kwargs) -> str:
        res, err = self.permission_check(kwargs)
        if not res:
            return err
        action = kwargs.pop("action", None)
        if action is None:
            return f"{self.err}: 缺少 action 参数"
        actions = {
            "read": self._read,
            "write": self._write,
            "delete": self._delete,
            "exists": self._exists,
            "isdir": self._isdir,
            "ls": self._ls,
            "read_image": self._read_image,
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

    def to_prompt(self) -> str:
        return (
            "- file: 文件操作工具\n"
            "  支持操作:\n"
            "    read(path: str)\n"
            "      path: 要读取的文件绝对路径\n"
            "    write(path: str, content: str, type: int)\n"
            "      path: 要写入的文件绝对路径（不存在会自动创建）\n"
            "      content: 要写入的文本内容，多行用 \\n 分隔\n"
            "      type: 写入模式，0=覆盖写入（默认），1=追加写入\n"
            "    delete(path: str)\n"
            "      path: 要删除的文件绝对路径\n"
            "    exists(path: str)\n"
            "      path: 要检查的文件或目录绝对路径\n"
            "    isdir(path: str)\n"
            "      path: 要判断是否是文件夹的路径\n"
            "    ls(path: str)\n"
            "      path: 要查看内容的目录绝对路径\n"
            "    read_image(path: str)\n"
            "      path: 要读取的图片绝对路径，支持 jpg/jpeg/png/gif/webp/bmp\n"
            "\n"
            "示例:\n"
            "<file><action>read</action><path>D:/AgentSpace/test.txt</path></file>\n"
            "<file><action>write</action><path>D:/AgentSpace/test.txt</path><content><![CDATA[内容写在这里]]></content><type>0</type></file>\n"
            "<file><action>delete</action><path>D:/AgentSpace/test.txt</path></file>\n"
            "<file><action>exists</action><path>D:/AgentSpace/test.txt</path></file>\n"
            "<file><action>isdir</action><path>D:/AgentSpace</path></file>\n"
            "<file><action>ls</action><path>D:/AgentSpace</path></file>\n"
            "<file><action>read_image</action><path>D:/AgentSpace/photo.jpg</path></file>"
        )