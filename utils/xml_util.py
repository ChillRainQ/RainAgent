import re

THOUGHT_TAG: str = "thought"
ACTION_TAG: str = "action"
OBSERVATION_TAG: str = "observation"
FINAL_ANSWER_TAG: str = "final_answer"
REPLY_TAG: str = "reply"
INVOKE_TAG: str = "invoke"


def parse_xml(text: str, tag: str) -> str | None:
    """
    Extract inner content of <tag>...</tag>.
    Lenient mode: if closing tag is missing, extract until the next known tag
    or end-of-text.
    """
    # strict first
    match = re.search(rf"<{tag}>(.*)</{tag}>", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    open_tag = f"<{tag}>"
    start = text.find(open_tag)
    if start == -1:
        return None
    start_content = start + len(open_tag)

    close_tag = f"</{tag}>"
    end = text.find(close_tag, start_content)
    if end != -1:
        return text[start_content:end].strip()

    # No closing tag: cut at the next known top-level tag if possible.
    sentinels = [
        f"<{THOUGHT_TAG}>",
        f"<{ACTION_TAG}>",
        f"<{OBSERVATION_TAG}>",
        f"<{FINAL_ANSWER_TAG}>",
        f"<{REPLY_TAG}>",
    ]
    next_pos = None
    for s in sentinels:
        p = text.find(s, start_content)
        if p != -1 and (next_pos is None or p < next_pos):
            next_pos = p
    if next_pos is None:
        return text[start_content:].strip()
    return text[start_content:next_pos].strip()


def has_tag(text: str, tag: str) -> bool:
    return bool(re.search(rf"<{tag}>", text))

if __name__ == "__main__":
    content = '...'
    print(repr(content))  # 看有没有特殊字符
    print(f"has reply: {has_tag(content, 'reply')}")
    print(f"REPLY_TAG value: '{REPLY_TAG}'")