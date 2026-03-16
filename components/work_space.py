import os

from system.config import AgentConfig


class WorkSpace:
    work_dir:str = None
    work_dir_list: str = None
    def __init__(self, config:AgentConfig):
        self.config = config
        pass

    def init(self):
        """
        初始化工作空间到Agent空间
        :return:
        """
        self.work_dir = self.config.get("agent_space").get("path")
        self.work_dir_list = os.listdir(self.work_dir)

    def update(self, work_dir:str):
        self.work_dir = work_dir
        self.work_dir_list = os.listdir(self.work_dir)

    @property
    def dir_to_prompt(self) -> str:
        if not self.work_dir:
            return "未设置"
        return self.work_dir

    @property
    def list_to_prompt(self) -> str:
        if not self.work_dir_list:
            return "（空目录）"
        return "\n".join(f"- {f}" for f in self.work_dir_list)