import subprocess
import sys
import tempfile
import os
from agent_tools.register import register, BaseTool


@register.register
class PythonCodeTool(BaseTool):
    name = "python"
    desc = "执行 Python 代码"

    def invoke(self, **kwargs) -> str:
        action = kwargs.pop("invoke", None) or kwargs.pop("action", None)
        actions = {
            "run": self._run,
            "run_file": self._run_file,
        }
        func = actions.get(action)
        if func is None:
            return f"{self.err}: 不支持的操作: {action}"
        try:
            return func(**kwargs)
        except Exception as e:
            return f"{self.err}: {e}"

    def _run(self, code: str, timeout: str = "30", **_) -> str:
        """执行代码字符串"""
        # 写入临时文件执行，避免 shell 注入
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(code)
            tmp_path = f.name
        try:
            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=int(timeout),
                encoding="utf-8",
                errors="replace",
            )
            output = result.stdout.strip()
            error = result.stderr.strip()
            if result.returncode != 0:
                return f"ERROR:\n{error}" if error else f"ERROR: 退出码 {result.returncode}"
            return output or "（无输出）"
        finally:
            os.unlink(tmp_path)

    def _run_file(self, path: str, timeout: str = "30", **_) -> str:
        """执行指定 Python 文件"""
        if not os.path.exists(path):
            return f"{self.err}: 文件不存在: {path}"
        result = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=int(timeout),
            encoding="utf-8",
            errors="replace",
        )
        output = result.stdout.strip()
        error = result.stderr.strip()
        if result.returncode != 0:
            return f"ERROR:\n{error}" if error else f"ERROR: 退出码 {result.returncode}"
        return output or "（无输出）"

    def to_prompt(self) -> str:
        return (
            "- code: 执行 Python 代码\n"
            "  支持操作:\n"
            "    run(code: str, timeout: int)       执行代码字符串，默认超时30秒\n"
            "    run_file(path: str, timeout: int)  执行指定 Python 文件\n"
            "\n"
            "示例:\n"
            "<python><invoke>run</invoke><code>print('hello world')</code></python>\n"
            "<python><invoke>run_file</invoke><path>D:/AgentSpace/test.py</path></python>\n"
        )