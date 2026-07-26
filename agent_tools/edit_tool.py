import os

from agent_tools.register import register, BaseTool
from utils import file_util, xml_util


@register.register
class EditTool(BaseTool):
    name = "edit"
    desc = "安全编辑工具（替换文本）"

    def invoke(self, **kwargs) -> str:
        res, err = self.permission_check(kwargs)
        if not res:
            return err

        action = kwargs.pop(xml_util.INVOKE_TAG, None)
        actions = {
            "replace": self._replace,
        }
        func = actions.get(action)
        if func is None:
            return f"{self.err}: 不支持的操作: {action}"
        try:
            return func(**kwargs)
        except Exception as e:
            return f"{self.err}: {e}"

    def _replace(self, path: str, old: str, new: str, count: str = "1", **_) -> str:
        if not os.path.exists(path):
            return f"{self.err}: 文件不存在: {path}"
        content = file_util.read_file(path)
        if content is None:
            return f"{self.err}: 读取失败: {path}"

        count_i = int(count)
        if old not in content:
            return f"{self.err}: 未找到要替换的文本"

        replaced = content.replace(old, new, count_i)
        if replaced == content:
            return f"{self.err}: 替换未生效"
        ok = file_util.write_file(path, replaced, type=0)
        return "成功" if ok else f"{self.err}: 写入失败"

    def to_prompt(self) -> str:
        return (
            "- edit: 安全编辑工具（替换文本）\n"
            "  支持操作:\n"
            "    replace(path: str, old: str, new: str, count: int)\n"
            "\n"
            "示例:\n"
            "<edit><invoke>replace</invoke><path>D:/AgentSpace/a.txt</path><old>foo</old><new>bar</new></edit>\n"
        )

