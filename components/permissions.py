import os
from pathlib import Path
from system.config import AgentConfig


class Permissions:
    permission_map: dict = {}
    pass_permission_map: dict = {}

    def __init__(self):
        pass

    def init(self, config):
        self.permission_map = config.get("permissions")
        no_perm_list = self.permission_map.get("no_permissions_area", [])
        # 兼容字符串和列表两种格式
        if isinstance(no_perm_list, str):
            no_perm_list = [no_perm_list]
        self.no_permissions_area = [Path(p) for p in no_perm_list if p]
        space = config.get("agent_space")
        self.space_path = Path(space.get("path", "")) if space else None

    def _is_in_no_permissions_area(self, path: str) -> bool:
        if not self.no_permissions_area:
            return False
        resolved_path = Path(path).resolve()
        for no_perm in self.no_permissions_area:
            try:
                resolved_path.relative_to(no_perm.resolve())
                return True
            except ValueError:
                continue
        return False

    def _is_in_space(self, path: str) -> bool:
        """是否在agent空间内"""
        if not self.space_path:
            return False
        try:
            Path(path).resolve().relative_to(self.space_path.resolve())
            return True
        except ValueError:
            return False

    def has_read_permission(self, action: str, path: str) -> tuple[bool, str]:
        """
        返回 (是否有权限, 原因)
        """
        if self._is_in_no_permissions_area(path):
            return False, f"⚠️ 路径 {path} 在禁止访问区域内"
        if self._is_in_space(path) and self.permission_map.get("space_file_read"):
            return True, ""
        if self.permission_map.get("all_file_read"):
            return True, ""
        if self.permission_map.get(action):
            return True, ""
        if self.permission_map.get("if_need_write_or_read_ask_me"):
            return self.ask_permission("read", path), "正在请求权限"
        return False, f"无读取权限: {path}"

    def has_write_permission(self, path: str) -> tuple[bool, str]:
        """
        返回 (是否有权限, 原因)
        """
        if self._is_in_no_permissions_area(path):
            return False, f"⚠️ 路径 {path} 在禁止访问区域内"
        if self._is_in_space(path) and self.permission_map.get("space_file_write"):
            return True, ""
        if self.permission_map.get("all_file_write"):
            return True, ""
        if self.permission_map.get("if_need_write_or_read_ask_me"):
            return self.ask_permission("write", path), "正在请求权限"
        return False, f"无写入权限: {path}"

    def has_internet_permission(self) -> tuple[bool, str]:
        """
        返回 (是否有权限, 原因)
        """
        if self.permission_map.get("internet"):
            return True, ""
        elif self.permission_map.get("if_need_internet_ask_me"):
            return self.ask_permission("internet", "internet"), "正在请求权限"
        return False, "⚠️ 网络访问权限已关闭"

    def ask_permission(self, permission_name: str, path) -> bool:
        """询问用户是否授权，返回是否同意"""
        if self.pass_permission_map.get(path):
            return True
        answer = input(f"⚠️ {permission_name}-Path:{path}，是否允许？(y/n):\n>>> ").strip().lower()
        res = answer in ["y", "Y", "允许", "是", "yes", "Yes", "YES"]
        if res:
            self.pass_permission_map[path] = permission_name
        return res


permissions = Permissions()
