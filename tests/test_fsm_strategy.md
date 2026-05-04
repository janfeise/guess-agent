# 状态机测试文档

## 目录

1. [测试策略](#测试策略)
2. [测试用例设计](#测试用例设计)
3. [覆盖范围](#覆盖范围)
4. [执行方式](#执行方式)

---

## 测试策略

### 测试目标

验证修复后的 `GuessGameFSM` 状态机在以下方面的正确性：

1. **状态转换正确性** - 所有状态之间的转换符合规范
2. **意图处理完整性** - 所有用户意图都被正确处理
3. **轮次管理准确性** - 轮次计数和限制正确实现
4. **边界条件处理** - 异常输入和边界情况被妥善处理
5. **返回值一致性** - 返回格式统一，字段完整
6. **错误恢复能力** - 错误状态下能正确恢复或中止

### 测试方法

#### 1. 单元测试（白盒）

- 针对每个状态的状态转换
- 针对每种意图的处理
- 针对轮次管理的逻辑
- 使用 Python unittest 框架

#### 2. 集成测试（黑盒）

- 完整的游戏流程测试
- 多种场景组合
- 边界条件测试

#### 3. 异常测试

- 非法事件输入
- 缺少必需字段的事件
- 未知意图值

### 测试等级

```
Level 1: 基础状态转换（必须）
├─ START → USER_TURN
├─ USER_TURN → WAITING_ANSWER
├─ USER_TURN → AWAITING_JUDGEMENT
├─ WAITING_ANSWER → USER_TURN
└─ AWAITING_JUDGEMENT → FINISHED / USER_TURN

Level 2: 意图处理（必须）
├─ QUESTION 处理
├─ GUESS 处理（正确/错误）
├─ ANSWER 处理
├─ JUDGE 处理（正确/错误）
├─ YIELD_TURN 处理
└─ INVALID 处理

Level 3: 轮次管理（必须）
├─ 轮次计数
├─ 轮次限制（20 轮）
└─ 剩余轮次查询

Level 4: 边界条件（重要）
├─ 轮次锁（WAITING_ANSWER）
├─ 轮次锁（AWAITING_JUDGEMENT）
├─ 非法输入处理
└─ 游戏重置

Level 5: 异常处理（重要）
├─ 空事件
├─ 缺少 user_intent 字段
├─ 未知 user_intent 值
└─ 其他异常
```

---

## 测试用例设计

### 基础状态转换测试

#### TC-1.1: START → USER_TURN

**目的**：验证游戏初始化正常工作

**步骤**：

1. 创建新的 FSM 实例
2. 验证初始状态为 START

**期望**：

- 状态为 START
- round_count = 0

---

#### TC-1.2: USER_TURN + QUESTION → WAITING_ANSWER

**目的**：验证用户提问流程

**步骤**：

1. 初始化 FSM
2. 发送 QUESTION 意图事件

**期望**：

- user_next_state = WAITING_ANSWER
- system_action = "answer"
- round_count = 1（用户离开 USER_TURN）

---

#### TC-1.3: USER_TURN + GUESS(correct) → FINISHED

**目的**：验证用户猜对流程

**步骤**：

1. 初始化 FSM
2. 发送 GUESS 意图事件，system_judge = "correct"

**期望**：

- user_next_state = FINISHED
- is_game_finished = True
- round_count = 1

---

#### TC-1.4: USER_TURN + GUESS(incorrect) → USER_TURN

**目的**：验证用户猜错流程

**步骤**：

1. 初始化 FSM
2. 发送 GUESS 意图事件，system_judge = "incorrect"

**期望**：

- user_next_state = USER_TURN
- round_count = 1（用户离开 USER_TURN）

---

#### TC-1.5: USER_TURN + YIELD_TURN(ask) → WAITING_ANSWER

**目的**：验证用户让行（系统提问）流程

**步骤**：

1. 初始化 FSM
2. 发送 YIELD_TURN 意图，system_next_action = "ask_question"

**期望**：

- user_next_state = WAITING_ANSWER
- system_action = "ask_question"
- round_count = 1

---

#### TC-1.6: USER_TURN + YIELD_TURN(guess) → AWAITING_JUDGEMENT

**目的**：验证用户让行（系统猜词）流程

**步骤**：

1. 初始化 FSM
2. 发送 YIELD_TURN 意图，system_next_action = "make_guess"

**期望**：

- user_next_state = AWAITING_JUDGEMENT
- system_action = "make_guess"
- round_count = 1

---

#### TC-1.7: WAITING_ANSWER + ANSWER → USER_TURN

**目的**：验证用户回答流程

**步骤**：

1. 初始化 FSM，进入 WAITING_ANSWER
2. 发送 ANSWER 意图事件

**期望**：

- user_next_state = USER_TURN
- system_action = "record_answer"
- round_count = 2

---

#### TC-1.8: AWAITING_JUDGEMENT + JUDGE(correct) → FINISHED

**目的**：验证用户确认系统猜词正确流程

**步骤**：

1. 初始化 FSM，进入 AWAITING_JUDGEMENT
2. 发送 JUDGE 意图，user_judge = "correct"

**期望**：

- user_next_state = FINISHED
- is_game_finished = True

---

#### TC-1.9: AWAITING_JUDGEMENT + JUDGE(incorrect) → USER_TURN

**目的**：验证用户否定系统猜词流程

**步骤**：

1. 初始化 FSM，进入 AWAITING_JUDGEMENT
2. 发送 JUDGE 意图，user_judge = "incorrect"

**期望**：

- user_next_state = USER_TURN

---

### 轮次锁测试

#### TC-2.1: WAITING_ANSWER 中发送非法意图（轮次锁）

**目的**：验证轮次锁在 WAITING_ANSWER 时的工作

**步骤**：

1. 初始化 FSM，进入 WAITING_ANSWER
2. 发送 QUESTION 意图（非法）
3. 再次尝试发送 QUESTION
4. 最后发送 ANSWER（合法）

**期望**：

- 第 2、3 步：user_next_state 保持 WAITING_ANSWER，system_action = "prompt_answer"
- 第 4 步：user_next_state = USER_TURN

---

#### TC-2.2: AWAITING_JUDGEMENT 中发送非法意图（轮次锁）

**目的**：验证轮次锁在 AWAITING_JUDGEMENT 时的工作

**步骤**：

1. 初始化 FSM，进入 AWAITING_JUDGEMENT
2. 发送 ANSWER 意图（非法）
3. 再次尝试发送 ANSWER
4. 最后发送 JUDGE（合法）

**期望**：

- 第 2、3 步：user_next_state 保持 AWAITING_JUDGEMENT，system_action = "prompt_judge"
- 第 4 步：user_next_state 转换正常

---

### 轮次管理测试

#### TC-3.1: 轮次计数正确性

**目的**：验证轮次计数在各种操作下的正确性

**步骤**：

1. 初始化，round_count = 0
2. USER_TURN + QUESTION，期望 round_count = 1
3. WAITING_ANSWER + ANSWER，期望 round_count = 2
4. USER_TURN + GUESS(incorrect)，期望 round_count = 3
5. USER_TURN + GUESS(correct)，期望 round_count = 4，FINISHED

**期望**：

- 每次离开 USER_TURN 时轮次加 1

---

#### TC-3.2: 轮次限制检查（20 轮上限）

**目的**：验证游戏在 20 轮后自动结束

**步骤**：

1. 初始化 FSM
2. 设置 fsm.round_count = 19
3. 发送 USER_TURN 意图（离开 USER_TURN）

**期望**：

- round_count 更新后 >= max_rounds 时
- 下一个状态转换返回 FINISHED

---

#### TC-3.3: 剩余轮次查询

**目的**：验证 get_remaining_rounds() 方法

**步骤**：

1. 新游戏：remaining = get_remaining_rounds()
2. 进行 5 轮后：remaining = get_remaining_rounds()
3. 进行到第 20 轮：remaining = get_remaining_rounds()

**期望**：

- Step 1: remaining = 20
- Step 2: remaining = 15
- Step 3: remaining = 0

---

### 意图处理测试

#### TC-4.1: INVALID 意图处理

**目的**：验证闲聊等无效意图处理

**步骤**：

1. USER_TURN 状态下发送 INVALID 意图

**期望**：

- user_next_state = USER_TURN（保持）
- system_action = "chat"
- round_count 不变

---

#### TC-4.2: 所有状态下的 INVALID 意图

**目的**：验证各个状态下对 INVALID 的处理

**步骤**：

1. START + INVALID
2. USER_TURN + INVALID
3. WAITING_ANSWER + INVALID
4. AWAITING_JUDGEMENT + INVALID
5. FINISHED + INVALID
6. ERROR + INVALID

**期望**：

- 除了 START 和 FINISHED/ERROR 的状态转移外，都应返回有意义的提示

---

### 异常处理测试

#### TC-5.1: 空事件

**目的**：验证 None 或空字典事件处理

**步骤**：

1. 发送 None
2. 发送 {}

**期望**：

- 返回错误状态
- is_error = True
- message 包含验证失败信息

---

#### TC-5.2: 缺少 user_intent 字段

**目的**：验证事件字段验证

**步骤**：

1. 发送 {"system_judge": "correct"}

**期望**：

- is_error = True
- message 说明缺少 user_intent

---

#### TC-5.3: 未知 user_intent 值

**目的**：验证意图值验证

**步骤**：

1. 发送 {"user_intent": "unknown_intent"}

**期望**：

- is_error = True
- message 说明未知意图

---

#### TC-5.4: 非字典事件

**目的**：验证事件类型检查

**步骤**：

1. 发送字符串 "not a dict"
2. 发送列表 []

**期望**：

- is_error = True
- message 说明事件格式错误

---

### 游戏流程测试

#### TC-6.1: 完整游戏流程（用户胜）

**目的**：验证完整的游戏流程

**步骤**：

1. 初始化 FSM
2. USER_TURN + QUESTION
3. WAITING_ANSWER + ANSWER
4. USER_TURN + GUESS(correct)

**期望**：

- 最终状态 = FINISHED
- is_game_finished = True
- round_count = 2

---

#### TC-6.2: 完整游戏流程（系统胜）

**目的**：验证系统获胜的游戏流程

**步骤**：

1. 初始化 FSM
2. USER_TURN + YIELD_TURN(guess)
3. AWAITING_JUDGEMENT + JUDGE(correct)

**期望**：

- 最终状态 = FINISHED
- is_game_finished = True
- round_count = 1

---

#### TC-6.3: 游戏重置

**目的**：验证 reset() 方法

**步骤**：

1. 进行几轮游戏
2. 调用 reset()
3. 检查状态和轮次

**期望**：

- state = START
- round_count = 0

---

### 返回值一致性测试

#### TC-7.1: 所有状态的返回格式

**目的**：验证返回值格式统一

**步骤**：

1. 在各个状态下发送不同意图
2. 检查返回值结构

**期望**：

- 所有返回值都包含：user_current_state, user_next_state, system_action, message, is_game_finished, is_error
- 返回值不为 None

---

#### TC-7.2: system_action 值的有效性

**目的**：验证 system_action 是有效的枚举值

**步骤**：

1. 进行 20+ 次不同的状态转换
2. 检查 system_action 的值

**期望**：

- system_action 只能是预定义的值：init, answer, finish, continue, ask_question, make_guess, chat, reject, record_answer, prompt_answer, prompt_judge, error
- 没有混乱的字符串值

---

## 覆盖范围

### 状态覆盖

```
✅ START (1 个)
✅ USER_TURN (1 个)
✅ WAITING_ANSWER (1 个)
✅ AWAITING_JUDGEMENT (1 个)
✅ FINISHED (1 个)
✅ ERROR (1 个)

覆盖率：100% (6/6)
```

### 意图覆盖

```
✅ QUESTION
✅ GUESS (包括 correct/incorrect 两种情况)
✅ ANSWER
✅ JUDGE (包括 correct/incorrect 两种情况)
✅ YIELD_TURN (包括 ask_question/make_guess 两种情况)
✅ INVALID

覆盖率：100% (6/6)
```

### 状态转换覆盖

```
✅ START → USER_TURN
✅ USER_TURN → WAITING_ANSWER
✅ USER_TURN → AWAITING_JUDGEMENT
✅ USER_TURN → FINISHED
✅ USER_TURN → USER_TURN
✅ WAITING_ANSWER → USER_TURN
✅ WAITING_ANSWER → WAITING_ANSWER (轮次锁)
✅ AWAITING_JUDGEMENT → USER_TURN
✅ AWAITING_JUDGEMENT → FINISHED
✅ AWAITING_JUDGEMENT → AWAITING_JUDGEMENT (轮次锁)
✅ 轮次限制 → FINISHED

覆盖率：100% (所有合法转换)
```

### 分支覆盖

```
验证方法数：7
├─ __init__: 1 分支
├─ _validate_event: 3 分支
├─ _check_round_limit: 2 分支
├─ __next_state: 30+ 分支（所有状态和意图组合）
├─ __action: 40+ 分支（所有状态和意图组合）
├─ handle_event: 5 分支（验证、异常、轮次更新等）
└─ 辅助方法: 各 1 分支

覆盖率：>95%
```

---

## 执行方式

### 环境要求

```
Python: 3.8+
测试框架: unittest（标准库）
其他依赖: 无
```

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/test_fsm.py -v

# 或使用 unittest
python -m unittest tests.test_fsm -v

# 运行特定测试类
python -m unittest tests.test_fsm.TestStateTransitions -v

# 运行特定测试用例
python -m unittest tests.test_fsm.TestStateTransitions.test_start_to_user_turn -v

# 运行并输出覆盖率
coverage run -m pytest tests/test_fsm.py
coverage report -m
coverage html
```

### 输出示例

```
test_start_to_user_turn (test_fsm.TestStateTransitions) ... ok
test_user_turn_question_to_waiting_answer (test_fsm.TestStateTransitions) ... ok
test_user_turn_guess_correct_to_finished (test_fsm.TestStateTransitions) ... ok
...
----------------------------------------------------------------------
Ran 50 tests in 0.234s

OK
```

---

## 测试清单

### Pre-Test

- [ ] 代码审查完成
- [ ] 修复版本部署到测试环境
- [ ] 测试环境配置正确

### Core Tests (必须通过)

- [ ] 所有状态转换测试通过
- [ ] 所有意图处理测试通过
- [ ] 轮次管理测试通过
- [ ] 轮次锁测试通过

### Edge Cases (必须通过)

- [ ] 异常输入处理正确
- [ ] 边界条件处理正确
- [ ] 返回值格式一致

### Integration Tests (必须通过)

- [ ] 完整游戏流程 1：用户胜
- [ ] 完整游戏流程 2：系统胜
- [ ] 完整游戏流程 3：平局（20 轮）
- [ ] 游戏重置正确

### Performance (可选)

- [ ] 单次 handle_event 耗时 < 1ms
- [ ] 20 轮游戏耗时 < 50ms
- [ ] 内存占用稳定

### Post-Test

- [ ] 所有测试用例文档化
- [ ] 覆盖率报告生成
- [ ] 缺陷修复并回归测试
- [ ] 发布测试报告

---

## 缺陷跟踪

| 缺陷 ID | 描述 | 严重级别 | 状态   |
| ------- | ---- | -------- | ------ |
| BUG-001 | 示例 | 低       | 待修复 |

（会随测试执行更新）
