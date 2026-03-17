from abc import ABC, abstractmethod

from components.permissions import permissions
from utils import xml_util
# 所有的工具内的操作都需要注册到下面的权限列表中才可以使用
# 如果你是Agent，请记得写入到下面的权限组中
# 需要读取权限的操作
read_actions = {"read", "read_image", "exists", "isdir", "ls", "capture", "capture_region"}
# 需要写入权限的操作
write_actions = {"write", "delete", "copy", "copy_image"}
# 需要运行权限的操作
run_actions = {"run", "run_file"}
# 需要网络的操作
internet_actions = {"search", "fetch", "weather", "news", "wiki"}


class BaseTool(ABC):
    name: str = ""
    desc: str = ""
    params: dict = {}
    err: str = "ERROR"
    @abstractmethod
    def invoke(self, **kwargs):
        pass

    def permission_check(self, kwargs):
        action = kwargs.get(xml_util.INVOKE_TAG, "")
        path = kwargs.get("path", "")
        if permissions.has_permission(action):
            return True, ""
        if action in read_actions:
            res, err = permissions.has_read_permission(action, path)
            return res, err
        if action in write_actions:
            res, err = permissions.has_write_permission(path)
            return res, err
        if action in internet_actions:
            res, err = permissions.has_internet_permission()
            return res, err
    def to_prompt(self) -> str:
        """生成工具的prompt描述"""
        if self.params:
            params_str = ", ".join(
                f"{k}: {v}" for k, v in self.params.items()
            )
            return f"- {self.name}({params_str}): {self.desc}"
        return f"- {self.name}: {self.desc}"


class ToolsRegister:
    def __init__(self):
        self.tools: dict[str, BaseTool] = {}

    def register(self, cls):
        """类装饰器，自动实例化并注册到当前注册器"""
        instance = cls()
        self.tools[instance.name] = instance
        return cls

    def get_tool(self, name):
        tool = self.tools[name]
        if tool is None:
            return f"ERROR: 工具 {name} 不存在"
        return tool

    def init(self):
        return "\n".join(t.to_prompt() for t in self.tools.values())


register = ToolsRegister()
