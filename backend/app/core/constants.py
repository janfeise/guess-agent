# 猜词约束与校验word

MAX_WORD_LENGTH = 10

def normalize_word(word: str) -> str:
    # 去除前后空格并转换为小写
    return word.strip().lower()

def validate_word(word: str) -> str:
    normalized_word = normalize_word(word)
    if len(normalized_word) == 0:
        raise ValueError("词不能为空")
    if len(normalized_word) > MAX_WORD_LENGTH:
        raise ValueError(f"输入的词语长度不能超过 {MAX_WORD_LENGTH} 个字符")
    return normalized_word

def validate_start_word(word: str) -> str:
    normalized_word = word.strip()
    if len(normalized_word) == 0:
        raise ValueError("词不能为空")
    if len(normalized_word) < 2 or len(normalized_word) > 6:
        raise ValueError("开局目标词长度必须在 2 到 6 个字符之间")

    forbidden_chars = [" ", "\n", "\r", "\t", "。", "，", "！", "？", ",", ".", ";", ":"]
    if any(ch in normalized_word for ch in forbidden_chars):
        raise ValueError("目标词不能包含标点或空白字符")

    return normalized_word