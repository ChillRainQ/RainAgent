import ollama

from core.config import LLMConfig, CoreConstant
from utils import template_util


class LLM:
    def __init__(self, config: LLMConfig):
        api_type = config.get("current") if config.get("current") is not None else config.get("default")
        llm_config = config.get(api_type)
        model_list = llm_config.get("list")
        self.constant = CoreConstant()
        self.model_name = model_list.get("current") if model_list.get("current") is not None else model_list.get(
            "default")
        self.model_config = model_list.get(self.model_name)
        self.url = self.model_config.get("url")
        self.ctx = self.model_config.get("ctx")
        self.api_key = self.model_config.get("api_key")
        self.temperature = self.model_config.get("temperature")
        if api_type == "local":
            self.client = ollama.Client(host=self.url)
        self.system_prompt = None
        self.user_prompt = None
        self.history = []

    def setup(self, system_prompt):
        self.system_prompt = system_prompt
        self._set_system_prompt(system_prompt)

    def _set_system_prompt(self, prompt: str):
        self.system_prompt = [self._build_message("system", prompt, None)]

    def _create_chat_task(self, message: str, images: str= None, think: bool = False):
        message = template_util.create_question_template(message)
        self._add_history("user", message, images=images)
        chat_content = []

        if self.system_prompt is not None:
            chat_content.extend(self.system_prompt)
            chat_content.extend(self.history)
        else:
            chat_content = self.history
        return chat_content
    def clear_history(self):
        """清空历史记录"""
        self.history = []

    def _add_history(self, role, message, images):
        self.history.append(self._build_message(role, message, images))

    def _chat_local(self, messages: dict | list, think: bool = False) -> str:
        """本地Ollama服务"""

        response = self.client.chat(
            model=self.model_name,
            messages=messages,
            think=think,
        )
        return response.message.content

    def chat(self, messages: str, images: str = None, think: bool = False):
        task = self._create_chat_task(messages, images, think)
        response = self._chat_local(task, think=think)
        self._add_history("assistant", response, None)
        return response

    def test(self):
        message = self._build_message('user', '你好', None)
        messages = [message]
        return self._chat_local(messages)

    def _build_message(self, role: str, text: str, images):
        message = {
            "role": role,
            "content": text,
        }
        if images:
            message["images"] = images
        return message


if __name__ == "__main__":
    config = LLMConfig()
    llm = LLM(config)
    print('llm loaded')
    while True:
        print(llm.chat(input()))
