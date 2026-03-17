import json
import re

from core.llm import LLM

PLAN_PROMPT = """你是一个任务规划器。
根据用户目标，将任务拆分为若干个可独立执行的步骤。

要求：
- 每个步骤是一个明确的、可执行的操作
- 如果是普通聊天（不需要工具），返回空数组 []
- 只输出 JSON 数组，不要输出任何其他内容，不要输出 markdown 代码块

输出格式：
[
  {"step": 1, "desc": "步骤描述"},
  {"step": 2, "desc": "步骤描述"}
]
"""
class Planer:
    llm: LLM = None
    def __init__(self):
        pass
    def init(self, llm: LLM):
        self.llm = llm

    def plan(self, target):
        msg = [
            {"role": "system", "content": PLAN_PROMPT},
            {"role": "user", "content": target},
        ]
        raw = self.llm._chat_local(msg)
        text = re.sub(r"```(?:json)?|```", "", raw).strip()
        try:
            return json.loads(text)
        except Exception:
            return []


if __name__ == "__main__":
    from core.config import LLMConfig
    from core.llm import LLM

    llm = LLM(LLMConfig())
    planer = Planer()
    planer.init(llm)

    tests = [
        "读取你专属目录的图片",   # 应该返回步骤
        "你好",                   # 应该返回 []
        "帮我读取 D:/test.txt 然后统计行数",  # 应该返回多步骤
    ]
    for t in tests:
        print(f"\n>>> 输入: {t}")
        result = planer.plan(t)
        print(f">>> 结果: {result}")