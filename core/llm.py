import ollama

from core.config import LLMConfig, CoreConstant
from system.constant import COMPRESS_PROMPT
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

    def _chat_local_stream(self, messages: list, think: bool = False):
        """流式生成器，逐token yield"""
        for chunk in self.client.chat(
                model=self.model_name,
                messages=messages,
                think=think,
                stream=True,
                options={
                    "num_ctx": self.ctx,
                    "temperature": self.temperature,
                    "num_keep": 0,
                }
        ):
            token = chunk.message.content
            if token:
                yield token

    def chat(self, messages: str, images=None, think: bool = False, stream: bool = False):
        task = self._create_chat_task(messages, images, think)  # 模板在里面构建

        if stream:
            def _stream_with_history():
                result = []
                for token in self._chat_local_stream(task, think=think):
                    result.append(token)
                    yield token
                self._add_history("assistant", "".join(result), images=None)

            return _stream_with_history()

        response = self._chat_local(task, think=think)
        self._add_history("assistant", response)
        return response
    # def chat(self, messages: str, images=None, think: bool = False, stream: bool = False):
    #     task = self._create_chat_task(messages, images, think)
    #
    #     if stream:
    #         def _stream_with_history():
    #             result = []
    #             for token in self._chat_local_stream(task, think=think):
    #                 result.append(token)
    #                 yield token
    #             # images 不存入 history，防止 base64 撑爆 context
    #             self._add_history("assistant", "".join(result), images=None)
    #
    #         return _stream_with_history()
    #
    #     response = self._chat_local(task, think=think)
    #     self._add_history("assistant", response, images=None)  # 同样不存图片
    #     return response

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

    def compress_history(self, keep_last: int = 2):
        """
        压缩历史记录
        keep_last: 保留最近几轮不压缩（保持短期记忆连贯）
        """
        if len(self.history) <= keep_last * 2:
            return  # 历史太短，不需要压缩

        # 最近 keep_last 轮保留，其余的压缩
        to_compress = self.history[:-keep_last * 2]
        to_keep = self.history[-keep_last * 2:]

        # 把待压缩部分格式化成文本
        history_text = "\n".join(
            f"{msg['role']}: {msg['content']}"
            for msg in to_compress
        )
        # 调用模型做摘要
        summary = self._chat_local([
            {"role": "system", "content": COMPRESS_PROMPT},
            {"role": "user", "content": history_text},
        ])
        print(f"[DEBUG] 历史压缩: {len(to_compress)} 条 → 1 条摘要")
        # 用摘要替换被压缩的部分
        summary_msg = self._build_message("user", f"[历史摘要]\n{summary}", None)
        self.history = [summary_msg] + to_keep


if __name__ == "__main__":
    config = LLMConfig()
    llm = LLM(config)
    print('llm loaded')
    while True:
        print(llm.chat(input()))
