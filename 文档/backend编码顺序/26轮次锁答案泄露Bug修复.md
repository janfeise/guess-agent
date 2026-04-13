# 轮次锁 Bug 修复：answer_reason 泄露答案 + action 字段不匹配

## 问题诊断

### 问题 1: result 字段泄露答案

**现象**：API 响应的 history 中，`result` 字段包含了"The user's question asks if the real answer '艺术史'..."，直接暴露了答案。

**原因**：

- `_handle_user_question()` 中使用了 LLM 返回的 `reason` 字段作为 `result`
- LLM 的 `reason` 包含了对问题的分析，会提到"答案是..."
- 这个 `result` 被完整地写入 history 并返回给客户端

**代码位置**：`_handle_user_question()` 第 487 行

```python
result=answer_reason or f"answer={answer_label}",  # ← answer_reason 来自 LLM 的 reason
```

### 问题 2: action 字段值不匹配导致错误的阶段转移

**现象**：

- 日志显示 `decide_agent_action` 返回 `"action": "ask"`（要求继续提问）
- 但 API 响应为 `"phase": "awaiting_judgement"`（进入猜测阶段）
- 第一轮提问就莫名其妙进入了猜测阶段，且 `system_guess` 为空

**原因**：

- `decide_agent_action` 返回的是 `"action": "ask" | "guess"`
- 代码检查的是 `if agent_action == "question"`（应该是 `"ask"`）
- 当 LLM 返回 `"action": "ask"` 时，与 `"question"` 不匹配，条件为 False
- 代码进入了 else 分支（猜测分支），导致错误的阶段转移

**代码位置**：

- `_handle_user_question()` 第 495 行
- `_handle_user_answer()` 第 630 行

```python
agent_action = agent_decision.get("action", "question")  # ← 默认值错误

if agent_action == "question":  # ← 检查错误，应该是 "ask"
    # 系统继续提问
else:
    # 系统猜测 ← 被错误地执行
```

## 修复方案

### 修复 1: 不使用 LLM reason 作为 result（避免泄露答案）

**位置**：`_handle_user_question()` 和 `_handle_user_answer()`

**修改**：

```python
# 之前
result=answer_reason or f"answer={answer_label}",

# 现在
result="user_asked_question",  # 只记录游戏事件，不包含 LLM reasoning
```

同样地，在 `_handle_user_answer()` 中：

```python
# 之前
result=(intent_result or {}).get("reason", ""),

# 现在
result="user_answer_recorded",
```

### 修复 2: action 字段匹配

**位置**：`_handle_user_question()` 和 `_handle_user_answer()`

**修改**：

```python
# 之前
agent_action = agent_decision.get("action", "question")
if agent_action == "question":

# 现在
agent_action = agent_decision.get("action", "ask")
if agent_action == "ask":
```

**为什么**：根据 `agent_decision.txt` 的提示词，返回的是 `"action": "ask | guess"`，不是 `"question | guess"`。

### 修复 3: 添加 sanitize_history_for_client() 方法

**位置**：`GameService` 类中

**作用**：清理返回给客户端的 history，移除所有 `result` 字段

```python
@staticmethod
def sanitize_history_for_client(history: list[dict]) -> list[dict]:
    """
    清理 history 中的敏感字段，避免向客户端泄露答案。
    移除 result 字段中包含的 LLM reasoning 和其他敏感信息。
    """
    sanitized = []
    for item in history:
        clean_item = dict(item)
        # 移除 result 字段（可能包含答案的推理过程）
        if "result" in clean_item:
            del clean_item["result"]
        sanitized.append(clean_item)
    return sanitized
```

### 修复 4: API 端点处理响应

**位置**：`backend/app/api/v1/submit_turn.py` 的 `submit_turn()` endpoint

**作用**：在返回响应前清理 history

```python
# 之前
return await service.submit_turn(game_id, user_text, request.mode, request.turn_type)

# 现在
result = await service.submit_turn(game_id, user_text, request.mode, request.turn_type)
# 清理 history 中的敏感信息（避免泄露答案）
if "history" in result and result["history"]:
    result["history"] = service.sanitize_history_for_client(result["history"])
return result
```

## 修改清单

### 文件 1: `backend/app/services/game_service.py`

| 改动                                       | 行号    | 说明                                                    |
| ------------------------------------------ | ------- | ------------------------------------------------------- |
| 添加 `sanitize_history_for_client()` 方法  | ~147    | 新增静态方法，用于清理 history                          |
| 修改 `_handle_user_question()` result 字段 | 487     | 改成 "user_asked_question" 而不是 answer_reason         |
| 修改 `_handle_user_question()` action 检查 | 495-496 | "question" → "ask"                                      |
| 修改 `_handle_user_answer()` result 字段   | 620     | 改成 "user_answer_recorded" 而不是 intent_result reason |
| 修改 `_handle_user_answer()` action 检查   | 630-631 | "question" → "ask"                                      |

### 文件 2: `backend/app/api/v1/submit_turn.py`

| 改动                          | 行号  | 说明                  |
| ----------------------------- | ----- | --------------------- |
| 修改 `submit_turn()` endpoint | 64-65 | 添加 history 清理逻辑 |

## 修复验证

### 修复 1 验证：result 字段不再泄露答案

**测试**：调用 submit_turn API，检查返回的 history

**修复前**：

```json
{
  "result": "The user's question asks if the real answer '艺术史' (Art History) is a science subject..."
}
```

**修复后**：

```json
{
  // result 字段被移除，只保留其他必要字段
}
```

### 修复 2 验证：第一轮不再错误进入猜测阶段

**测试**：创建游戏并提问，观察返回的 phase 和日志

**修复前**：

```
日志: decide_agent_action 返回 action: "ask"
响应: phase: "awaiting_judgement"  ← 错误！应该是 awaiting_answer
响应: system_guess: ""  ← 空的猜测词
消息: "我猜你想的词是：。对吗？"  ← 猜测词为空
```

**修复后**：

```
日志: decide_agent_action 返回 action: "ask"
响应: phase: "awaiting_answer"  ← 正确！
响应: system_question: "它是不是一个具体的物体？"  ← 系统的下一个问题
消息: "我的下一个问题是：它是不是一个具体的物体？"  ← 显示系统问题
```

## 性能影响

- **零性能开销**：修复只是修改了字段名和条件检查，没有额外的计算或 LLM 调用

## 安全性改进

- ✅ 防止了答案泄露（result 字段）
- ✅ 确保了正确的游戏流程（action 字段匹配）
- ✅ clients 看不到 internal LLM reasoning
- ✅ history 仅包含必要的游戏数据

## 后续建议

### 1. 增强 result 字段标准化

未来可以考虑为所有 result 字段使用预定义的常量，而不是硬编码字符串：

```python
class GameEventType:
    USER_ASKED_QUESTION = "user_asked_question"
    USER_ANSWERED = "user_answer_recorded"
    SYSTEM_ASKS_QUESTION = "system_asks_question"
    SYSTEM_MAKES_GUESS = "system_makes_guess"
    # ...
```

### 2. 添加日志审计

监控所有可能泄露答案的操作：

```python
if "艺术史" in result or "答案" in result:
    logger.warning("Potential answer leak detected in result field")
```

### 3. 自动化测试

添加单元测试确保 history 清理的正确性：

```python
def test_sanitize_history_removes_result_field():
    history = [{"round_no": 1, "result": "answer=yes", "input_text": "..."}]
    cleaned = GameService.sanitize_history_for_client(history)
    assert "result" not in cleaned[0]
    assert "input_text" in cleaned[0]
```

## 总结

▶️ **问题 1（答案泄露）**：

- ❌ 原因：result 字段使用了 LLM 的敏感 reasoning
- ✅ 修复：改用安全的游戏事件描述，并在 API 层清理

▶️ **问题 2（错误阶段转移）**：

- ❌ 原因：action 字段检查不匹配（"question" vs "ask"）
- ✅ 修复：改成检查 "ask"，与 LLM 返回格式一致

▶️ **验证**：

- ✅ 无语法错误
- ✅ 修复后第一轮正确进入 awaiting_answer
- ✅ history 不包含敏感信息
- ✅ system_question 正确显示
