疑问：猜词agent项目中，核心是llm api，llm api 是项目的大脑，应该控制整个项目的运转，但是项目中只能根据api返回的结果进行下一步动作，因此对于api返回的格式应该进行控制？如：

1. 游戏是否结束应该有llm api确定，因为程序不可能判别用户输入的是提问的语句还是猜词的词
2. 猜测：
   猜测分为用户猜测和agent猜测

- 用户猜测，每轮只有一次对话机会，如果进行猜测则消耗对话机会，即用户猜测，系统回答用户是否猜测正确，若猜测错误，则系统进入下一步，即系统提问（1. 系统回答是否猜测正确 2. 猜测错误系统进入提问）
- 系统猜测：如何设计系统是否猜测呢？系统进行猜测，用户判断是否猜测正确，如果猜测错误，系统提示用户可以进行提问了

你的思路已经进入到这个项目最关键的一层了：**谁在“控制流程”**

先直接给你结论，再展开设计：

```text
❌ 不要让 LLM 完全控制流程（危险且不可控）
✅ 让 LLM 负责“理解与决策”，程序负责“状态与流程控制”
```

也就是说：

```text
LLM = 大脑（判断意图、生成内容）
程序 = 操作系统（控制游戏状态机）
```

---

# 一、核心问题本质

你现在遇到的关键矛盾是：

```text
用户输入是自由文本 → 程序无法判断类型
```

例如：

- “它是不是计算机相关？”（提问）
- “是编译器吗？”（猜测）
- “我猜是操作系统”（猜测）
- “给我点提示”（违规/无效）

👉 传统代码确实很难稳定判断

---

# 二、正确解法：让 LLM 输出“结构化结果”

你已经意识到关键点了：

```text
必须约束 LLM 返回格式（非常正确）
```

---

## 统一返回结构（核心设计）

建议你定义一个**标准协议（JSON）**

```json
{
  "intent": "question | guess | invalid",
  "content": "用户原始意图解析",
  "answer": "yes | no | unknown",
  "guess_result": "correct | wrong | none",
  "game_status": "continue | end",
  "next_action": "user_turn | agent_turn"
}
```

---

# 三、第一点：游戏是否结束由谁决定

你的原想法：

```text
由 LLM 判断游戏是否结束
```

👉 需要修正：

```text
✔ LLM 判断“是否猜中”
✔ 程序决定“是否结束游戏”
```

---

## 正确分工

### LLM负责：

```json
{
  "intent": "guess",
  "guess_result": "correct"
}
```

### 程序负责：

```python
if guess_result == "correct":
    game_status = "end"
```

---

# 四、用户行为设计（你的规则优化版）

## 用户回合

```text
用户输入 → LLM解析 → 程序执行
```

---

### 情况1：用户提问

```json
{
  "intent": "question",
  "answer": "yes"
}
```

程序：

```text
记录 → 切换到 agent 回合
```

---

### 情况2：用户猜测

```json
{
  "intent": "guess",
  "guess_result": "wrong"
}
```

程序执行：

```text
1. 返回：猜错
2. 扣除本轮机会
3. 切换到 agent 回合
```

---

### 情况3：猜对

```json
{
  "intent": "guess",
  "guess_result": "correct"
}
```

程序：

```text
结束游戏
```

---

# 五、Agent猜测设计（重点回答你）

你问的核心：

```text
系统什么时候猜？
```

---

## 推荐设计：概率触发 + 条件触发

不要每轮都猜

---

## 方案一：规则驱动（推荐）

```text
当满足以下条件时，Agent才猜：

1. 已有信息足够（轮数 > N）
2. LLM判断“有较高置信度”
```

---

## LLM返回结构扩展

```json
{
  "intent": "agent_action",
  "action": "ask | guess",
  "confidence": 0.82,
  "guess_word": "编译器"
}
```

---

## 程序控制

```python
if action == "guess" and confidence > 0.8:
    执行猜测
else:
    继续提问
```

---

# 六、Agent猜测流程（完整）

## Step 1：Agent决定行为

```json
{
  "action": "guess",
  "guess_word": "操作系统",
  "confidence": 0.85
}
```

---

## Step 2：系统展示给用户

```text
系统猜测：操作系统
是否正确？
```

---

## Step 3：用户判断

```text
✔ 正确 → 游戏结束
✖ 错误 → 进入用户回合
```

---

# 七、完整状态机（非常关键）

```text
用户回合
  ↓
LLM解析（question / guess）
  ↓
程序执行
  ↓
切换到Agent回合
  ↓
Agent决策（ask / guess）
  ↓
执行
  ↓
返回用户
```

---

# 八、最关键的 Prompt（结构化输出）

## 用户输入解析 Prompt

```text
你是一个猜词游戏的裁判系统。

请分析用户输入，并返回JSON格式结果：

规则：

1. 判断用户意图：
   - question（是/否问题）
   - guess（猜测答案）
   - invalid（无效输入）

2. 如果是猜测：
   - 判断是否猜中

返回格式：

{
  "intent": "...",
  "answer": "...",
  "guess_result": "...",
  "extracted_guess": "..."
}

只返回JSON，不要解释
```

---

## Agent决策 Prompt

```text
你是猜词游戏中的AI玩家。

请根据当前信息决定：

1. 提问（ask）
2. 猜测（guess）

返回JSON：

{
  "action": "ask | guess",
  "question": "...",
  "guess_word": "...",
  "confidence": 0-1
}

只返回JSON
```

---

# 九、一个关键设计原则（非常重要）

```text
LLM负责“理解世界”
程序负责“改变世界”
```

---

# 十、一句话总结

```text
不要让 LLM 控制流程，让 LLM 说“该做什么”，程序决定“是否执行”
```

---

如果你下一步继续推进，我可以帮你直接写出：

- 完整 JSON 协议定义（前后端统一）
- FastAPI 接口设计（/ask /guess /agent-turn）
- Agent 防作弊 Prompt（避免偷看答案）

这一步已经是从“能跑”进化到“可控系统”的关键阶段了

下面给你一套**可直接落地的完整 Prompt 体系（生产可用级）**，已经按照你的项目架构拆分为三个核心能力：

```text
1. 用户输入解析（裁判）
2. Agent决策（AI玩家）
3. 初始化生成答案
```

并且全部采用**结构化 JSON 输出**，方便 FastAPI 直接解析使用

---

# 一、用户输入解析 Prompt（最关键）

👉 作用：解决你最核心的问题
👉 判断：提问 / 猜测 / 无效输入

---

## Prompt（裁判系统）

```text
你是一个“猜词游戏”的裁判系统。

你的任务是：分析用户输入，并严格返回结构化JSON结果。

【游戏规则】
- 用户每轮只能做一件事：提问 或 猜测
- 提问必须是“是/否”问题
- 猜测是用户认为答案是什么
- 不能返回解释，只能返回JSON

【你需要完成的任务】

1. 判断用户意图 intent：
   - "question"：是/否提问
   - "guess"：猜测答案
   - "invalid"：无效输入（如闲聊、提示请求）

2. 如果是提问：
   - 提取标准化问题（question）

3. 如果是猜测：
   - 提取猜测词（guess_word）
   - 判断是否猜中（根据提供的答案）

4. 返回JSON格式如下：

{
  "intent": "question | guess | invalid",
  "question": "...",
  "guess_word": "...",
  "guess_result": "correct | wrong | none",
  "reason": "简要说明（不超过20字）"
}

【输入信息】

当前答案（仅用于判断是否猜中）：
{answer}

用户输入：
{user_input}

【输出要求】

- 必须是合法JSON
- 不允许输出解释
- 不允许多余文本
- 字段必须完整（没有填 null）
```

---

# 二、Agent决策 Prompt（AI玩家）

👉 作用：控制 AI 行为（提问 or 猜测）

---

## Prompt（Agent）

```text
你是一个“猜词游戏”的AI玩家。

你的目标是：通过最少轮次猜出用户的答案。

【游戏规则】

- 每轮你只能执行一个动作：
  1. 提问（ask）：提出一个是/否问题
  2. 猜测（guess）：直接猜答案

- 提问要求：
  - 必须是“是/否”问题
  - 必须基于已有信息逐步缩小范围

- 猜测要求：
  - 只有在“高度确定”时才猜
  - 不要频繁猜测

【决策策略】

- 如果信息不足 → 提问
- 如果信息充分 → 猜测
- 目标是减少轮数，而不是乱猜

【输入信息】

历史对话（按时间顺序）：
{history}

当前已知信息总结：
{context_summary}

【输出格式（必须严格JSON）】

{
  "action": "ask | guess",
  "question": "...",
  "guess_word": "...",
  "confidence": 0.0~1.0,
  "reason": "简要决策原因（不超过20字）"
}

【约束】

- 只能返回JSON
- 不允许解释
- 不允许多余字段
- question 和 guess_word 只能填一个（另一个填 ""）
```

---

# 三、初始化生成词 Prompt

👉 作用：生成 Agent 的答案（受控随机）

---

## Prompt（生成词）

```text
你正在参与一个“猜词游戏”的初始化阶段。

请生成一个用于猜词游戏的目标词。

【要求】

1. 必须是一个“名词”
2. 必须属于指定学科领域
3. 难度适中：
   - 不能过于简单
   - 不能过于冷门
4. 长度：2~6个字
5. 不要解释
6. 只返回词语

【输入】

学科领域：{subject}
难度：{difficulty}
已使用词：{history_words}

【输出要求】

- 只返回一个词
- 不允许任何解释或符号
```

---

# 四、系统回答 Prompt（回答用户问题）

👉 作用：Agent回答“是/否”

---

## Prompt（回答）

```text
你是猜词游戏中的裁判。

请根据“真实答案”回答用户问题。

【规则】

- 只能回答：
  - "是"
  - "否"
  - "无法确定"

- 不允许解释
- 不允许泄露答案
- 必须严格客观

【输入】

真实答案：
{answer}

用户问题：
{question}

【输出】

只返回：是 / 否 / 无法确定
```

---

# 五、推荐 JSON 统一协议（强烈建议）

后端统一用这个结构：

```json
{
  "intent": "question | guess | invalid",
  "question": "",
  "guess_word": "",
  "guess_result": "correct | wrong | none",
  "answer": "yes | no | unknown",
  "action": "ask | guess",
  "confidence": 0.0
}
```

---

# 六、FastAPI 使用示例（关键落地）

```python
import json

def call_llm(prompt):
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(resp.choices[0].message.content)
```

---

# 七、关键工程建议（避免翻车）

## 1. 强制 JSON 校验

```python
try:
    data = json.loads(resp)
except:
    重试 or fallback
```

---

## 2. 设置 temperature

```python
temperature = 0.3
```

👉 保证稳定性

---

## 3. 加一层“兜底逻辑”

```python
if intent not in ["question", "guess"]:
    intent = "invalid"
```

---

# 八、最终结构（你整个系统会变成）

```text
用户输入
  ↓
LLM（裁判）→ intent
  ↓
程序控制流程
  ↓
LLM（Agent决策）
  ↓
执行动作
```

---

# 九、一句话总结

```text
Prompt的本质不是“让AI回答”，而是“让AI输出可执行指令”
```

---

如果你下一步继续推进，我可以帮你直接做：

- 完整 FastAPI 接口（/game/start /game/turn /agent/turn）
- 游戏状态机代码（可直接运行）
- 前端如何消费 JSON（Vue 实现）

现在这套 Prompt 已经可以直接进入开发阶段了
