import os


RESOURCES_DIR: str = 'resources'
CURRENT_PATH: str = os.path.dirname(os.path.abspath(__file__))
PROJECT_PATH: str = os.path.dirname(CURRENT_PATH)
RESOURCES_PATH: str = os.path.join(PROJECT_PATH, RESOURCES_DIR)
SYSTEM_PROMPT_TEXT_FILE_NAME: str = 'system_prompt.txt'
SYSTEM_PROMPT_TEXT_LAST_FILE_NAME: str = 'system_prompt_last_used.txt'
SYSTEM_PROMPT_TEXT_PATH: str = os.path.join(RESOURCES_PATH, SYSTEM_PROMPT_TEXT_FILE_NAME)
SYSTEM_PROMPT_TEXT_LAST_FILE_PATH: str = os.path.join(RESOURCES_PATH, SYSTEM_PROMPT_TEXT_LAST_FILE_NAME)
AGENT_CONFIG_NAME: str = "agent_config.yaml"
AGENT_CONFIG_PATH: str = os.path.join(RESOURCES_PATH, AGENT_CONFIG_NAME)
AGENT_SPACE_NAME: str = "agent_space"
AGENT_SPACE_PATH: str = os.path.join(PROJECT_PATH, AGENT_SPACE_NAME)