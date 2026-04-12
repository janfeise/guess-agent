# 流式传输

def build_stream_event(event_type: str, content: str | None = None) -> dict:
    # 构建一个流式传输事件的字典，包含事件类型和内容
    return {
        "event": event_type,
        "content": content or "",
    }

def build_stream_start() -> dict:
    # 构建一个表示流式传输开始的事件
    return build_stream_event("start")

def build_stream_chunk(content: str) -> dict:
    # 构建一个表示流式传输数据块的事件，包含数据内容
    return build_stream_event("chunk", content)

def build_stream_end() -> dict:
    # 构建一个表示流式传输结束的事件
    return build_stream_event("end")

def build_stream_error(error_message: str) -> dict:
    # 构建一个表示流式传输错误的事件，包含错误信息
    return build_stream_event("error", error_message)