from system import constant
from utils.file_util import read_config


class AgentConfig:
    def __init__(self):
        self.config = read_config(constant.AGENT_CONFIG_PATH)

    def get(self, name: str):
        return self.config.get(name)