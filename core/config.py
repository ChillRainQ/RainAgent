import os

from utils.file_util import read_config


class CoreConstant:
    LLM_CONFIG_NAME: str = 'llm_config.yaml'
    RESOURCES_DIR: str = 'resources'
    CURRENT_PATH: str = os.path.dirname(os.path.abspath(__file__))
    PROJECT_PATH: str = os.path.dirname(CURRENT_PATH)
    RESOURCES_PATH: str = os.path.join(PROJECT_PATH, RESOURCES_DIR)
    LLM_CONFIG_PATH: str = os.path.join(RESOURCES_PATH, LLM_CONFIG_NAME)
    # QUESTION_TEMPLATE: str = "<question>{user_input}</question>"


class LLMConfig:
    def __init__(self):
        self.config = read_config(CoreConstant.LLM_CONFIG_PATH)


    def get(self, name: str):
        return self.config.get(name)
