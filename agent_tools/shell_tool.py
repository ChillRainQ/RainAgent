import os
import subprocess

from agent_tools.register import register, BaseTool
from system.config import AgentConfig
from utils import xml_util


def _safe_cwd(cwd: str | None) -> str | None:
    if not cwd:
        return None
    return os.path.abspath(cwd)


@register.register
class ShellTool(BaseTool):
    name = "shell"
    desc = "执行系统命令（短任务）"

    def __init__(self):
        self._config = AgentConfig()
        self._default_cwd = self._config.get("agent_space").get("path")

    def invoke(self, **kwargs) -> str:
        res, err = self.permission_check(kwargs)
        if not res:
            return err

        action = kwargs.pop(xml_util.INVOKE_TAG, None)
        if action != "run":
            return f"{self.err}: 不支持的操作: {action}"
        try:
            return self._run(**kwargs)
        except subprocess.TimeoutExpired:
            return f"{self.err}: 命令执行超时"
        except Exception as e:
            return f"{self.err}: {e}"

    def _run(
        self,
        cmd: str,
        cwd: str | None = None,
        timeout: str = "30",
        **_,
    ) -> str:
        cwd = _safe_cwd(cwd) or self._default_cwd
        if cwd and not os.path.isdir(cwd):
            return f"{self.err}: cwd 不是目录: {cwd}"

        # On Windows, shell=True is often required for builtins and user commands.
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=int(timeout),
            encoding="utf-8",
            errors="replace",
        )
        out = (result.stdout or "").strip()
        err = (result.stderr or "").strip()
        if result.returncode != 0:
            details = err or out
            return f"{self.err}: exit_code={result.returncode}\n{details}".strip()
        return out or "（无输出）"

    def to_prompt(self) -> str:
        return (
            "- shell: 执行系统命令（短任务）\n"
            "  支持操作:\n"
            "    run(cmd: str, cwd: str, timeout: int)\n"
            "      cwd: 可选，默认 AgentSpace\n"
            "\n"
            "示例:\n"
            "<shell><invoke>run</invoke><cmd>dir</cmd><cwd>D:/AgentSpace</cwd></shell>\n"
            "<shell><invoke>run</invoke><cmd>python -m py_compile main.py</cmd></shell>\n"
        )

