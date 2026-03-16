import re

THOUGHT_TAG: str = "thought"
ACTION_TAG: str = "action"
OBSERVATION_TAG: str = "observation"
FINAL_ANSWER_TAG: str = "final_answer"
REPLY_TAG: str = "reply"


def parse_xml(text: str, tag: str) -> str | None:
    match = re.search(rf"<{tag}>(.*)</{tag}>", text, re.DOTALL)
    return match.group(1).strip() if match else None


def has_tag(text: str, tag: str) -> bool:
    return bool(re.search(rf"<{tag}>", text))

if __name__ == "__main__":
    content = '...'
    print(repr(content))  # 看有没有特殊字符
    print(f"has reply: {has_tag(content, 'reply')}")
    print(f"REPLY_TAG value: '{REPLY_TAG}'")