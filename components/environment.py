import os
import platform

from system.config import AgentConfig


class SystemEnvironment:
    def __init__(self, config):
        self.system = platform.system()  # Windows / Linux / Darwin
        self.version = platform.version()  # 系统版本
        self.machine = platform.machine()  # x86_64 / ARM
        self.python_version = platform.python_version()
        self.agent_space = config.get("agent_space").get("path")
        self.user = os.getenv("USERNAME") or os.getenv("USER")

    def init(self, config: AgentConfig):
        pass
    @property
    def to_prompt(self) -> str:
        return (
            f"操作系统: {self.system} {self.version}\n"
            f"架构: {self.machine}\n"
            f"Python: {self.python_version}\n"
            f"用户: {self.user}\n"
            f"AgentSpace: {self.agent_space}\n"
        )

    def __repr__(self):
        return f"SystemEnvironment(system={self.system}, user={self.user}, agent_space={self.agent_space})"
