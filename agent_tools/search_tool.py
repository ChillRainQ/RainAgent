import fnmatch
import os
import re

from agent_tools.register import register, BaseTool
from utils import xml_util


def _iter_files(root: str, file_glob: str | None = None):
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip common heavy dirs
        dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__", ".venv", "venv", "node_modules"}]
        for name in filenames:
            if file_glob and not fnmatch.fnmatch(name, file_glob):
                continue
            yield os.path.join(dirpath, name)


@register.register
class SearchTool(BaseTool):
    name = "search"
    desc = "代码/文件检索工具（grep/glob）"

    def invoke(self, **kwargs) -> str:
        res, err = self.permission_check(kwargs)
        if not res:
            return err

        action = kwargs.pop(xml_util.INVOKE_TAG, None)
        actions = {
            "grep": self._grep,
            "glob": self._glob,
        }
        func = actions.get(action)
        if func is None:
            return f"{self.err}: 不支持的操作: {action}"
        try:
            return func(**kwargs)
        except re.error as e:
            return f"{self.err}: 正则错误: {e}"
        except Exception as e:
            return f"{self.err}: {e}"

    def _glob(self, pattern: str, path: str, max_results: str = "200", **_) -> str:
        root = os.path.abspath(path)
        if not os.path.exists(root):
            return f"{self.err}: 路径不存在: {root}"

        max_results_i = int(max_results)
        results = []
        if os.path.isfile(root):
            base = os.path.basename(root)
            if fnmatch.fnmatch(base, pattern):
                return root
            return "（无匹配）"

        for full in _iter_files(root):
            if fnmatch.fnmatch(os.path.basename(full), pattern):
                results.append(full)
                if len(results) >= max_results_i:
                    break
        return "\n".join(results) if results else "（无匹配）"

    def _grep(
        self,
        pattern: str,
        path: str,
        file_glob: str | None = None,
        max_results: str = "200",
        ignore_case: str = "false",
        **_,
    ) -> str:
        root = os.path.abspath(path)
        if not os.path.exists(root):
            return f"{self.err}: 路径不存在: {root}"

        flags = re.MULTILINE
        if str(ignore_case).lower() in ("1", "true", "yes", "y"):
            flags |= re.IGNORECASE
        rx = re.compile(pattern, flags)

        max_results_i = int(max_results)
        hits = []

        files = [root] if os.path.isfile(root) else list(_iter_files(root, file_glob=file_glob))
        for fp in files:
            # best-effort text read
            try:
                with open(fp, "r", encoding="utf-8", errors="replace") as f:
                    for i, line in enumerate(f, start=1):
                        if rx.search(line):
                            hits.append(f"{fp}:{i}:{line.rstrip()}")
                            if len(hits) >= max_results_i:
                                return "\n".join(hits)
            except OSError:
                continue

        return "\n".join(hits) if hits else "（无匹配）"

    def to_prompt(self) -> str:
        return (
            "- search: 代码/文件检索工具\n"
            "  支持操作:\n"
            "    glob(pattern: str, path: str, max_results: int)\n"
            "    grep(pattern: str, path: str, file_glob: str, max_results: int, ignore_case: bool)\n"
            "\n"
            "示例:\n"
            "<search><invoke>glob</invoke><pattern>*.py</pattern><path>D:/PythonCode/RainAgent</path></search>\n"
            "<search><invoke>grep</invoke><pattern>class\\\\s+LLM</pattern><path>D:/PythonCode/RainAgent</path><file_glob>*.py</file_glob></search>\n"
        )

