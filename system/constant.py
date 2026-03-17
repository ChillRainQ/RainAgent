import os


RESOURCES_DIR: str = 'resources'
CURRENT_PATH: str = os.path.dirname(os.path.abspath(__file__))
PROJECT_PATH: str = os.path.dirname(CURRENT_PATH)
RESOURCES_PATH: str = os.path.join(PROJECT_PATH, RESOURCES_DIR)
SYSTEM_PROMPT_TEXT_FILE_NAME: str = 'system_prompt.txt'
EXECUTE_PROMPT_TEXT_FILE_NAME: str = 'execute_prompt.txt'
SYSTEM_PROMPT_TEXT_LAST_FILE_NAME: str = 'system_prompt_last_used.txt'
SYSTEM_PROMPT_TEXT_PATH: str = os.path.join(RESOURCES_PATH, SYSTEM_PROMPT_TEXT_FILE_NAME)
EXECUTE_PROMPT_TEXT_PATH: str = os.path.join(RESOURCES_PATH, EXECUTE_PROMPT_TEXT_FILE_NAME)
SYSTEM_PROMPT_TEXT_LAST_FILE_PATH: str = os.path.join(RESOURCES_PATH, SYSTEM_PROMPT_TEXT_LAST_FILE_NAME)
AGENT_CONFIG_NAME: str = "agent_config.yaml"
AGENT_CONFIG_PATH: str = os.path.join(RESOURCES_PATH, AGENT_CONFIG_NAME)
AGENT_SPACE_NAME: str = "agent_space"
AGENT_SPACE_PATH: str = os.path.join(PROJECT_PATH, AGENT_SPACE_NAME)
COMPRESS_PROMPT = """你是一个对话摘要器。
将以下对话历史压缩为一段简短的摘要，保留关键信息和结论，去掉过程细节。
只输出摘要内容，不要输出任何其他内容。
"""