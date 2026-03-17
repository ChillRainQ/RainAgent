from core.llm import LLM

SUMMARY_PROMPT = """你是一个结果汇总器。
根据用户目标和各步骤执行结果，给出最终的完整回答。
语气风格：俏皮傲娇，但结果要准确完整。
只输出最终答案内容，不需要任何标签包裹。
"""


class Summarizer:
    llm: LLM = None

    def __init__(self):
        pass

    def init(self, llm: LLM):
        self.llm = llm

    def summarize(self, goal: str, history: list[dict]) -> str:
        history_text = "\n".join(
            f"步骤{item['step']} ({item['desc']}):\n{item['result']}"
            for item in history
        )
        msg = [
            {"role": "system", "content": SUMMARY_PROMPT},
            {"role": "user", "content": f"用户目标：{goal}\n\n执行结果：\n{history_text}"},
        ]
        return self.llm._chat_local(msg)
