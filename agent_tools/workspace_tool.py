from agent_tools.register import register, BaseTool
from main import work_space

@register.register
class WorkspaceTool(BaseTool):
    name = "workspace"
    desc = "工作空间管理工具"

    def __init__(self):
        # self.workspace = work_space
        pass

    def invoke(self, **kwargs) -> str:

        action = kwargs.pop("action", None)
        if action is None:
            return f"{self.err}: 缺少 action 参数"
        actions = {
            "cd": self._cd,
            "ls": self._ls,
            "pwd": self._pwd,
        }
        func = actions.get(action)
        if func is None:
            return f"{self.err}: 不支持的操作: {action}"
        try:
            return func(**kwargs)
        except Exception as e:
            return f"{self.err}: {e}"

    def _cd(self, path: str) -> str:
        """切换工作目录"""
        work_space.update(path)
        return f"已切换到: {work_space.work_dir}"

    def _ls(self) -> str:
        """列出当前工作目录内容"""
        return work_space.list_to_prompt

    def _pwd(self) -> str:
        """查看当前工作目录"""
        return work_space.dir_to_prompt

    def to_prompt(self) -> str:
        return (
            "- workspace: 工作空间管理工具\n"
            "  支持操作:\n"
            "    cd(path: str)\n"
            "\n"
            "示例:\n"
            "<workspace><action>cd</action><path>D:/AgentSpace</path></workspace>\n"
        )