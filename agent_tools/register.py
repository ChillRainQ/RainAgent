from abc import ABC, abstractmethod

from components.permissions import permissions

# 需要读取权限的操作
read_actions = {"read", "read_image", "exists", "isdir", "ls"}
# 需要写入权限的操作
write_actions = {"write", "delete"}
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
        action = kwargs.get("action", "")
        path = kwargs.get("path", "")
        if action in read_actions:
            res, err = permissions.has_read_permission(path)
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
            raise Exception(f"ERROR: 工具 {name} 不存在")
        return tool

    def init(self):
        return "\n".join(t.to_prompt() for t in self.tools.values())


register = ToolsRegister()
