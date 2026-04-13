# 19 LLM 响应解析与异常处理修复手册

## 1. 文档目标

这份手册解决的问题是：

**当 `POST /api/v1/games/{game_id}/turns` 已经调用到 LLM，甚至日志显示“LLM api 调用成功”，但接口仍然返回 500 时，应该怎么修。**

它和 [18普通问题回合500修复手册.md](18普通问题回合500修复手册.md) 不是重复关系。

- 18 号文档解决的是普通问题回合主链路缺失、状态机不完整的问题。
- 19 号文档解决的是 LLM 已经成功，但响应解析、异常传播和日志可观测性仍然不完整的问题。

---

## 2. 这个 500 的真实根因

这类 500 通常不是“模型没返回”，而是下面几类问题叠加导致的：

1. Agent 层把 LLM 原始内容当 JSON 解析，但模型实际返回的是普通文本或带代码块的 JSON。
2. `GuessAgent` 缺少统一的 `_parse_json_response()`，导致 `parse_user_intent()`、`answer_question()`、`decide_agent_action()` 在返回格式稍有偏差时直接抛异常。
3. `GameService` 在状态判断、猜词比较、数据库写回等位置没有统一打日志，异常只会一路冒泡到路由层。
4. 路由层只有一句笼统的 `Failed to submit turn`，没有 `game_id`、`phase`、`turn_type`、堆栈信息，排查时只能看到 500。

---

## 3. 本次修复做了什么

### 3.1 Agent 层

文件：[backend/app/agents/guess_agent_fixed.py](../../backend/app/agents/guess_agent_fixed.py)

新增了：

- `_parse_json_response()`：支持直接 JSON 和 Markdown 代码块 JSON。
- `parse_user_intent()`、`answer_question()`、`decide_agent_action()` 的异常兜底。
- `logger.exception(...)` 和 `logger.warning(...)`，让模型返回异常时能留下可读日志。

这一步的目标不是“让模型一定输出标准 JSON”，而是“即使模型输出不标准，也不要直接炸成 500”。
当前路由入口已经切到这个稳定实现文件；旧的 [guess_agent.py](../../backend/app/agents/guess_agent.py) 只作为残留实现保留，不再作为入口使用。

### 3.2 Service 层

文件：[backend/app/services/game_service.py](../../backend/app/services/game_service.py)

新增了：

- 回合请求入口日志。
- 阶段日志：`user_turn`、`awaiting_judgement`、猜词分支。
- 数据库存储前后的日志。
- repository 更新失败时的 `logger.exception(...)`。
- `is_guess_correct()` 的静态方法引用修复，避免用户猜词路径出现 NameError。

### 3.3 路由层

文件：[backend/app/api/v1/submit_turn.py](../../backend/app/api/v1/submit_turn.py)

新增了：

- 请求进入日志，包含 `game_id`、`turn_type`、`mode`、输入摘要。
- `ValueError` 的业务错误日志。
- 其他异常的堆栈日志。

这样后端即使返回 500，也能在日志里定位到具体是哪一层出了问题。

---

## 4. 日志约定

### 4.1 该记录什么

建议至少记录这些字段：

- `game_id`
- `turn_type`
- `mode`
- `phase`
- `history_len`
- `intent`
- `action`
- `pending_guess`
- `round_count`

### 4.2 不该记录什么

不要把这些内容直接打到日志里：

- `system_word`
- `system_password_encrypted`
- 任何明文密钥
- 完整的用户敏感输入全文，除非调试时临时打开并且确认不会外泄

### 4.3 推荐日志级别

- `INFO`：进入请求、阶段切换、LLM 决策完成、数据库更新成功。
- `WARNING`：输入无效、模型输出不符合预期但已经走兜底。
- `ERROR` / `exception`：LLM 调用失败、JSON 解析失败、数据库更新失败。

---

## 5. 推荐排查顺序

当再次出现“LLM 成功但接口 500”时，按这个顺序查：

1. 先看路由层日志，确认 `game_id`、`turn_type`、`mode`。
2. 再看 `GameService` 的阶段日志，确认当前是否进入 `awaiting_judgement` 或普通提问分支。
3. 再看 `GuessAgent` 的解析日志，确认是模型调用失败、空返回，还是 JSON 解析失败。
4. 最后查 repository 更新日志，确认是否卡在 MongoDB 写回。

---

## 6. 验证方式

### 6.1 正常问题

发送一次普通问题，确认：

- `submit_turn` 有请求进入日志。
- `GameService` 有 `phase` 和 `history_len` 日志。
- Agent 能返回 `answer` 和下一步动作。
- 数据库里的 `history`、`summary`、`round_count` 能更新。

### 6.2 猜词问题

发送一次用户猜词，确认：

- `is_guess_correct()` 不再因为静态方法调用错误抛异常。
- 猜对时会结束游戏。
- 猜错时会写回历史并恢复到 `user_turn`。

### 6.3 模型返回异常

模拟一个非 JSON 返回，确认：

- Agent 走兜底，不直接抛异常。
- 路由层仍可返回业务结果或可定位的 500。
- 日志里能看到解析失败的具体原因。

---

## 7. 结论

这次修复的核心不是“把 500 改成别的状态码”，而是：

- 让 LLM 输出不稳定时有兜底。
- 让 service 的状态流转有日志。
- 让路由层的 500 可追踪。

只要这三层都收口，后续再出现问题，就能快速定位是在 LLM、解析、状态机还是数据库写回。
