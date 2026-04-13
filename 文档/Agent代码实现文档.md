# Agent代码实现文档

## 1. 文档目标

本文档是一份偏“直接落地”的 Agent 代码实现文档，目标是帮助你在当前项目中真正写出可运行、可维护、可扩展的 Agent 层代码。

本文档会重点说明：

- Agent 层代码如何组织
- prompt 文件如何抽离并加载
- LangChain 如何在当前项目中落地
- 流式输出如何实现
- 短期记忆、长期记忆与上下文窗口如何设计
- 主模型与小助手如何分离
- 如何与 Service 层、Repository 层联动

本文档不是最终代码，但其中的代码示例已经尽量接近可以直接实现的结构。

---

## 2. 当前项目中的 Agent 角色

在这个项目中，Agent 不是一个普通聊天接口，而是整个猜词游戏的推理引擎。

### 2.1 主模型职责

主模型负责：

- 猜词推理
- 结合当前局历史回答问题
- 严格遵守游戏规则
- 不泄露答案
- 支持流式输出

### 2.2 小助手职责

小助手负责：

- 查询知识
- 提供解释
- 给出提问建议
- 不参与答案推理
- 不影响游戏公平

### 2.3 记忆职责

Agent 的记忆不是“无限聊天”，而是“按 game_id 管理当前局上下文”。

- 每局游戏独立
- 同一局游戏共享历史
- 上下文要截断
- 旧内容要摘要

---

## 3. 建议目录结构

### 3.1 Agent 层目录

```bash
backend/
└── app/
    └── agents/
        ├── guess_agent.py
        ├── prompt/
        │   ├── guess_system.txt
        │   ├── helper_system.txt
        │   └── game_rule.txt
        └── utils/
            ├── prompt_loader.py
            ├── memory_policy.py
            └── streaming.py
```

### 3.2 文件职责

- `guess_agent.py`：Agent 主类，负责统一组织模型调用
- `prompt/*.txt`：系统提示词文件
- `prompt_loader.py`：统一加载 prompt 文件
- `memory_policy.py`：统一控制上下文窗口和摘要策略
- `streaming.py`：封装流式事件输出格式

---

## 4. 依赖建议

Agent 层建议依赖这些包：

- `langchain`
- `langchain-openai`
- `pydantic`
- `pydantic-settings`
- `python-dotenv`

如果你使用的是 DeepSeek 兼容 OpenAI 协议，一般可以通过 `ChatOpenAI` 兼容接入。

---

## 5. prompt 文件实现

### 5.1 主模型 prompt

主模型 prompt 建议写成一个单独文本文件，例如 `guess_system.txt`。

示例内容：

```text
你是猜词游戏 Agent。
你必须严格遵守游戏规则。
你不能直接泄露答案。
你只能基于当前局历史和规则进行推理。
回答要简洁、稳定、克制。
```

### 5.2 小助手 prompt

示例内容：

```text
你是用户侧小助手。
你的任务是提供知识查询、解释和提示建议。
你不能参与答案推理。
你不能影响游戏公平。
你不能直接访问答案明文。
```

### 5.3 游戏规则 prompt

示例内容：

```text
猜词游戏规则：
1. 只能回答当前局内容相关问题。
2. 不能透露答案明文。
3. 回答必须简洁明确。
4. 只能基于当前上下文推理。
5. 不允许破坏游戏公平。
```

### 5.4 为什么要拆开

把 prompt 拆开是为了：

- 让规则可独立调整
- 让主模型和小助手分别拥有不同策略
- 让后续修改更方便
- 让 prompt 变成配置，而不是硬编码逻辑

---

## 6. prompt 加载器实现

### 6.1 设计目标

prompt 加载器的目标是：

- 给 Agent 提供统一读取入口
- 支持按文件名加载 prompt
- 文件不存在时给出明确错误
- 保持编码统一

### 6.2 推荐实现方式

```python
from pathlib import Path


class PromptLoader:
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)

    def load(self, filename: str) -> str:
        file_path = self.base_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {file_path}")
        return file_path.read_text(encoding="utf-8").strip()
```

### 6.3 设计说明

这个加载器的作用就是把 prompt 从“硬编码文本”变成“可配置文本”。

后续如果你要替换模型策略，只需要改 prompt 文件，不需要改 Agent 主体逻辑。

---

## 7. 记忆策略实现

### 7.1 设计目标

记忆策略的目标是：

- 按 game_id 管理上下文
- 只保留当前局有用的内容
- 对过长上下文进行截断
- 对更早内容进行摘要压缩

### 7.2 推荐实现方式

```python
class MemoryPolicy:
    def __init__(self, max_rounds: int = 8):
        self.max_rounds = max_rounds

    def build_recent_history(self, history: list[dict]) -> list[dict]:
        if len(history) <= self.max_rounds:
            return history
        return history[-self.max_rounds:]

    def build_summary(self, history: list[dict]) -> str:
        old_history = history[:-self.max_rounds]
        if not old_history:
            return ""
        return "；".join(
            f"Q:{item.get('question', '')} A:{item.get('answer', '')}"
            for item in old_history
        )
```

### 7.3 设计说明

这里的核心原则是：

- 最近轮次直接喂给模型
- 更早轮次变成摘要
- 摘要不是完整复述，而是帮助模型保留推理线索

### 7.4 当前项目中的使用建议

建议默认策略：

- 最近 6 到 10 轮直接保留
- 更早历史压缩成一段摘要
- 摘要放到 system prompt 后或上下文前部

---

## 8. 流式输出实现

### 8.1 设计目标

流式输出的目标是让前端可以逐段接收模型生成内容，而不是等待完整回答后再一次性返回。

### 8.2 推荐事件格式

建议定义如下事件：

- `start`：开始生成
- `chunk`：单段内容
- `end`：生成结束
- `error`：生成异常

### 8.3 推荐实现方式

```python
def build_stream_event(event_type: str, content: str | None = None) -> dict:
    return {
        "type": event_type,
        "content": content or "",
    }
```

### 8.4 FastAPI 侧通常配合 SSE

Agent 只负责把流式 token 或事件吐出去，真正返回给前端时，一般由 FastAPI 用 SSE 方式包装。

---

## 9. GuessAgent 主类实现

### 9.1 设计目标

`GuessAgent` 是整个 Agent 层的统一入口，建议它负责：

- 读取配置
- 初始化主模型和小助手模型
- 加载 prompt
- 组织上下文
- 支持普通调用
- 支持流式调用
- 支持摘要生成

### 9.2 推荐类结构

```python
class GuessAgent:
    def __init__(self, settings, prompt_loader, memory_policy):
        self.settings = settings
        self.prompt_loader = prompt_loader
        self.memory_policy = memory_policy
        self.agent_model = self._build_agent_model()
        self.helper_model = self._build_helper_model()

    def _build_agent_model(self):
        pass

    def _build_helper_model(self):
        pass

    def _load_prompt(self, mode: str):
        pass

    def _build_messages(self, question: str, history: list[dict], mode: str):
        pass

    async def answer(self, question: str, history: list[dict], mode: str = "agent"):
        pass

    async def stream_answer(self, question: str, history: list[dict], mode: str = "agent"):
        pass
```

### 9.3 类设计说明

#### 初始化时做什么

初始化时就把模型构建好，这样每次请求时不用重复创建对象。

#### 方法层面做什么

- `_build_agent_model()`：构建主模型
- `_build_helper_model()`：构建小助手模型
- `_load_prompt()`：读取 prompt 文件
- `_build_messages()`：把 prompt、历史、当前问题拼成消息
- `answer()`：普通回答
- `stream_answer()`：流式回答

### 9.4 推荐模型构建方式

如果你使用 OpenAI 兼容接口，可以使用类似下面的方式构建：

```python
# 这里只展示思路，不作为最终代码复制
ChatOpenAI(
    api_key=...,
    base_url=...,
    model=...,
    temperature=...
)
```

### 9.5 方法级实现说明

这一节把 `GuessAgent` 里每个方法具体应该怎么写、为什么这样写讲清楚。

#### 9.5.1 `__init__()`

这个方法负责完成对象初始化，建议只做三件事：

1. 保存外部注入的配置和工具
2. 构建主模型和小助手模型
3. 准备后续调用会使用的基础组件

设计考虑：

- 把模型初始化放在构造阶段，可以避免每次请求重复创建客户端
- 把 prompt 加载器、记忆策略作为依赖注入，方便测试和替换
- 让主模型和小助手都在类创建时准备好，后续切换 mode 只需要选模型，不需要重建

#### 9.5.2 `_build_agent_model()`

这个方法只负责创建主模型实例，不负责请求处理。

建议它完成的工作：

- 从配置中读取主模型参数
- 根据兼容接口创建模型对象
- 返回主模型实例

设计考虑：

- 主模型是游戏推理核心，应该在这里单独构造
- 如果未来更换模型，只改这里的构造逻辑即可
- 这个方法不要包含 prompt、历史、业务判断

#### 9.5.3 `_build_helper_model()`

这个方法只负责创建小助手模型实例。

建议它完成的工作：

- 从配置中读取小助手模型参数
- 创建独立模型对象
- 返回小助手实例

设计考虑：

- 小助手的职责和主模型不同，所以配置、prompt、温度策略都应独立
- 小助手不能直接复用主模型的推理规则
- 后续如果要单独调小助手能力，也只改这里和对应 prompt

#### 9.5.4 `_load_prompt(mode)`

这个方法负责根据 `mode` 读取对应 prompt。

建议它完成的工作：

- 判断当前是主模型还是小助手
- 选择对应 prompt 文件名
- 通过 prompt loader 读取文件内容
- 返回最终系统提示词

设计考虑：

- prompt 应该是可配置内容，而不是硬编码在类里
- 不同模式下的 prompt 需要保持隔离
- 如果 prompt 文件缺失，要尽早报错，而不是到模型调用时才失败

#### 9.5.5 `_build_messages(question, history, mode)`

这个方法负责把所有输入组装成模型可以使用的消息列表。

建议它完成的工作：

- 调用 `_load_prompt()` 获取 system prompt
- 调用记忆策略截断当前局历史
- 生成规则摘要或上下文摘要
- 把历史对话和当前问题按顺序组装成消息

设计考虑：

- 消息顺序会影响模型理解效果，所以顺序要固定
- 先放规则，再放历史，再放当前问题
- 上下文要裁剪，不要无限增长
- 主模型和小助手可以共用组装方式，但 prompt 不能共用

#### 9.5.6 `answer(question, history, mode)`

这个方法负责普通非流式回答。

建议它完成的工作：

- 调用 `_build_messages()`
- 选择当前模式对应的模型实例
- 发起一次性请求
- 拿到完整回答
- 做基础清理
- 返回给 Service 层

设计考虑：

- 这个方法适合先做成最稳的版本
- 先把普通回答跑通，再加流式
- 如果后面出现异常，应该向 Service 层抛出可读错误，而不是吞掉

#### 9.5.7 `stream_answer(question, history, mode)`

这个方法负责流式回答。

建议它完成的工作：

- 调用 `_build_messages()`
- 选择模型流式接口
- 逐段读取 token 或 chunk
- 按 SSE 事件格式输出
- 在结束时发出 end 事件

设计考虑：

- 流式输出必须保证事件顺序
- 如果中途出错，要输出 error 事件
- 流式返回的内容不应该改变核心业务逻辑，只是改变输出方式

#### 9.5.8 `_build_model_result()` 或统一结果整理

如果你后续希望让普通调用和流式调用返回一致结构，建议单独增加一个结果整理层。

它可以负责：

- 清理多余空白
- 统一输出格式
- 整理日志信息
- 区分普通结果和流式结果

设计考虑：

- 统一输出结构，Service 层会更容易接入
- 前端也更容易解析

---

---

## 10. 消息组装方式

### 10.1 消息顺序

消息顺序应该固定为：

1. system prompt
2. 游戏规则摘要
3. 当前局最近历史
4. 当前问题

### 10.2 为什么要这样排

- system prompt 决定角色和规则
- 游戏规则摘要强化约束
- 历史消息提供上下文
- 当前问题是本轮真正需要回答的内容

### 10.3 推荐消息策略

- 主模型消息更偏推理
- 小助手消息更偏解释
- 两者共用组装流程，但 prompt 不同

---

## 11. 普通调用实现

### 11.1 设计目标

先保证非流式回答能跑通，再做流式。

### 11.2 推荐流程

1. 读取 prompt
2. 截断历史
3. 组装消息
4. 调用模型
5. 清理返回文本
6. 交给 Service 层

### 11.3 结果处理

建议对模型结果做基本清理：

- 去掉首尾空白
- 统一多余换行
- 保持输出简洁

---

## 12. 流式调用实现

### 12.1 设计目标

流式调用要能边生成边返回，适合前端聊天界面。

### 12.2 推荐流程

1. 构造消息
2. 调用模型流式接口
3. 每次拿到 token 就输出一个事件
4. 最后输出结束事件

### 12.3 注意事项

- 不要先聚合成完整答案再输出
- 最后要保证有结束标记
- 错误时要输出 error 事件

---

## 13. 主模型与小助手的切换

### 13.1 mode 设计

建议通过 `mode` 参数控制调用哪一个模型。

可取值：

- `agent`：主模型
- `helper`：小助手

### 13.2 切换原则

- 主模型只用于游戏推理
- 小助手只用于知识查询和提示
- 两者共享框架，不共享策略文本

---

## 14. 详细实现步骤

### 14.1 第一步：先准备 prompt 文件

把主模型、小助手、游戏规则 prompt 文件准备好。

### 14.2 第二步：写 prompt 加载器

让 Agent 能统一读取 prompt 文件。

### 14.3 第三步：写记忆策略

先确定最近保留多少轮，旧历史如何摘要。

### 14.4 第四步：写模型构建函数

分别构建主模型和小助手模型。

### 14.5 第五步：写普通回答

先确认模型能正常返回结果。

### 14.6 第六步：写流式回答

再把普通回答扩展成流式。

### 14.7 第七步：接 Service 层

由 Service 层决定什么时候调用 Agent、什么时候保存结果。

### 14.8 第八步：补方法级职责说明

如果你准备真正实现代码，建议把每个方法的职责单独写在注释或文档里，至少明确：

- 初始化阶段做什么
- 模型构建阶段做什么
- prompt 读取阶段做什么
- 消息组装阶段做什么
- 普通调用阶段做什么
- 流式调用阶段做什么

这样可以避免后面写着写着把一个方法写成“什么都干”的大函数。

---

## 15. 典型代码示例

### 15.1 prompt 加载器

```python
from pathlib import Path


class PromptLoader:
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)

    def load(self, filename: str) -> str:
        file_path = self.base_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {file_path}")
        return file_path.read_text(encoding="utf-8").strip()
```

### 15.2 记忆策略

```python
class MemoryPolicy:
    def __init__(self, max_rounds: int = 8):
        self.max_rounds = max_rounds

    def build_recent_history(self, history: list[dict]) -> list[dict]:
        if len(history) <= self.max_rounds:
            return history
        return history[-self.max_rounds:]
```

### 15.3 流式事件

```python
def build_stream_event(event_type: str, content: str | None = None) -> dict:
    return {
        "type": event_type,
        "content": content or "",
    }
```

### 15.4 Agent 类结构

```python
class GuessAgent:
    def __init__(self, settings, prompt_loader, memory_policy):
        self.settings = settings
        self.prompt_loader = prompt_loader
        self.memory_policy = memory_policy
```

### 15.5 方法实现清单

如果你打算按方法逐个实现，建议优先顺序如下：

1. `__init__()`：先把依赖和模型准备好
2. `_build_agent_model()`：先保证主模型可初始化
3. `_build_helper_model()`：再保证小助手可初始化
4. `_load_prompt()`：让 prompt 文件能被读取
5. `_build_messages()`：确认消息能正确拼接
6. `answer()`：先跑通一次性回答
7. `stream_answer()`：最后再接流式输出

### 15.6 每个方法的设计考虑

- `__init__()`：避免运行时重复初始化，降低请求开销
- `_build_agent_model()`：主模型推理和小助手推理解耦
- `_build_helper_model()`：小助手单独配置，便于调整
- `_load_prompt()`：prompt 变成可维护配置
- `_build_messages()`：上下文和规则统一组装
- `answer()`：先建立稳定可用的基础链路
- `stream_answer()`：在基础链路稳定后再增加体验优化

---

## 16. 与当前项目的联动方式

### 16.1 与 Service 层联动

Service 层传入：

- game_id
- question
- history
- mode

Agent 返回：

- answer
- stream
- summary

### 16.2 与 Repository 层联动

Repository 层负责取出历史和保存回合，Agent 不直接碰数据库。

### 16.3 与前端联动

如果前端需要实时显示模型回答，建议使用 SSE 接收流式事件。

---

## 17. 实践规范

### 17.1 建议做法

- prompt 独立文件
- 主模型和小助手分开配置
- 每局游戏按 game_id 隔离
- 先普通调用后流式调用
- 长历史先摘要后喂给模型

### 17.2 不建议做法

- prompt 写死在类里
- 所有历史直接堆给模型
- 主模型和小助手共用一套规则文本
- Agent 同时负责写数据库和调模型

---

## 18. 验收标准

完成后，Agent 层至少应该满足：

- prompt 文件可修改
- 主模型和小助手可分离
- 同一局历史不会串线
- 普通回答可用
- 流式输出可用
- 上下文会裁剪
- 摘要能力可预留

---

## 19. 结论

Agent 层的核心不是“写一个会说话的类”，而是“写一个能控制模型行为的系统模块”。

如果你把 prompt、记忆、流式、模型切换都设计清楚，后面整个项目的 Agent 扩展会非常顺。

---

## 20. 详细代码实现参考

这一节给出更贴近实际编码的参考实现。它不是唯一写法，但非常适合当前项目的结构。

### 20.1 `prompt_loader.py`

这个文件负责统一读取 prompt 文件，避免把 prompt 写死在业务代码里。

```python
from pathlib import Path


class PromptLoader:
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)

    def load(self, filename: str) -> str:
        file_path = self.base_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {file_path}")
        return file_path.read_text(encoding="utf-8").strip()
```

#### 20.1.1 为什么这样写

- `Path` 让路径拼接更稳定
- `load()` 只负责一件事：读取文件
- 找不到文件时直接报错，方便尽早发现问题

#### 20.1.2 使用方式

```python
prompt_loader = PromptLoader(base_dir="app/agents/prompt")
system_prompt = prompt_loader.load("guess_system.txt")
```

---

### 20.2 `memory_policy.py`

这个文件负责控制上下文长度、历史截断和摘要策略。

```python
class MemoryPolicy:
    def __init__(self, max_rounds: int = 8):
        self.max_rounds = max_rounds

    def build_recent_history(self, history: list[dict]) -> list[dict]:
        if len(history) <= self.max_rounds:
            return history
        return history[-self.max_rounds:]

    def build_summary(self, history: list[dict]) -> str:
        old_history = history[:-self.max_rounds]
        if not old_history:
            return ""

        summary_parts: list[str] = []
        for item in old_history:
            question = item.get("question", "")
            answer = item.get("answer", "")
            summary_parts.append(f"Q:{question} A:{answer}")

        return "；".join(summary_parts)
```

#### 20.2.1 为什么这样写

- `build_recent_history()` 只保留最近轮次，避免上下文无限增长
- `build_summary()` 把更早历史压缩成摘要，帮助模型保留核心线索
- 摘要不是完整回放，而是推理辅助信息

#### 20.2.2 当前项目中的推荐值

- `max_rounds=8` 是一个比较稳妥的默认值
- 如果回答质量下降，可以调到 6
- 如果模型上下文足够长，可以调到 10

---

### 20.3 `streaming.py`

这个文件负责统一流式事件格式，方便 FastAPI 和前端对接。

```python
def build_stream_event(event_type: str, content: str | None = None) -> dict:
    return {
        "type": event_type,
        "content": content or "",
    }


def build_stream_start() -> dict:
    return build_stream_event("start")


def build_stream_chunk(content: str) -> dict:
    return build_stream_event("chunk", content)


def build_stream_end() -> dict:
    return build_stream_event("end")


def build_stream_error(message: str) -> dict:
    return build_stream_event("error", message)
```

#### 20.3.1 为什么这样写

- 统一事件结构，前端更容易解析
- 事件类型固定，便于调试和日志追踪
- 后续如果换 WebSocket，也能沿用同一套事件格式

---

### 20.4 `guess_agent.py` 主类参考实现

下面给出一个更接近真实项目的代码骨架。

```python
from pathlib import Path

from langchain_openai import ChatOpenAI

from app.agents.utils.memory_policy import MemoryPolicy
from app.agents.utils.prompt_loader import PromptLoader
from app.agents.utils.streaming import (
    build_stream_chunk,
    build_stream_end,
    build_stream_error,
    build_stream_start,
)


class GuessAgent:
    def __init__(self, settings, prompt_loader: PromptLoader, memory_policy: MemoryPolicy):
        self.settings = settings
        self.prompt_loader = prompt_loader
        self.memory_policy = memory_policy
        self.agent_model = self._build_agent_model()
        self.helper_model = self._build_helper_model()

    def _build_agent_model(self):
        return ChatOpenAI(
            api_key=self.settings.agent_model_api_key,
            base_url=self.settings.agent_model_base_url,
            model=self.settings.agent_model_name,
            temperature=self.settings.agent_model_temperature,
            streaming=True,
        )

    def _build_helper_model(self):
        return ChatOpenAI(
            api_key=self.settings.helper_model_api_key,
            base_url=self.settings.helper_model_base_url,
            model=self.settings.helper_model_name,
            temperature=self.settings.helper_model_temperature,
            streaming=True,
        )

    def _load_prompt(self, mode: str):
        if mode == "helper":
            return self.prompt_loader.load("helper_system.txt")
        return self.prompt_loader.load("guess_system.txt")

    def _build_messages(self, question: str, history: list[dict], mode: str):
        system_prompt = self._load_prompt(mode)
        recent_history = self.memory_policy.build_recent_history(history)
        summary = self.memory_policy.build_summary(history)

        messages: list[dict] = []
        messages.append({"role": "system", "content": system_prompt})

        if summary:
            messages.append({"role": "system", "content": f"历史摘要：{summary}"})

        for item in recent_history:
            user_question = item.get("question", "")
            assistant_answer = item.get("answer", "")
            messages.append({"role": "user", "content": user_question})
            messages.append({"role": "assistant", "content": assistant_answer})

        messages.append({"role": "user", "content": question})
        return messages

    def _select_model(self, mode: str):
        if mode == "helper":
            return self.helper_model
        return self.agent_model

    def _normalize_answer(self, answer: str) -> str:
        return answer.strip()

    async def answer(self, question: str, history: list[dict], mode: str = "agent"):
        messages = self._build_messages(question, history, mode)
        model = self._select_model(mode)

        response = await model.ainvoke(messages)
        final_answer = self._normalize_answer(str(response.content))

        return {
            "answer": final_answer,
            "history": history,
        }

    async def stream_answer(self, question: str, history: list[dict], mode: str = "agent"):
        messages = self._build_messages(question, history, mode)
        model = self._select_model(mode)

        yield build_stream_start()

        try:
            full_answer_parts: list[str] = []
            async for chunk in model.astream(messages):
                content = getattr(chunk, "content", "")
                if not content:
                    continue
                full_answer_parts.append(content)
                yield build_stream_chunk(content)

            yield build_stream_end()

        except Exception as exc:
            yield build_stream_error(str(exc))
```

#### 20.4.1 `__init__()` 的实现说明

初始化阶段做三件事：

1. 保存配置和工具依赖
2. 预先构建主模型
3. 预先构建小助手模型

这样每次请求进来时，不用重复创建模型对象。

#### 20.4.2 `_build_agent_model()` 的实现说明

这个方法负责构建主模型。

关键点：

- `streaming=True`：让模型支持流式输出
- `api_key`、`base_url`、`model`、`temperature` 全部来自配置
- 该方法不处理业务逻辑，只做模型创建

#### 20.4.3 `_build_helper_model()` 的实现说明

这个方法负责构建小助手模型。

和主模型一样，它只负责实例化，不负责业务判断。

#### 20.4.4 `_load_prompt()` 的实现说明

通过 `mode` 决定读取哪个 prompt 文件：

- `agent` -> `guess_system.txt`
- `helper` -> `helper_system.txt`

如果你后面还需要更多模式，也可以继续扩展这个方法。

#### 20.4.5 `_build_messages()` 的实现说明

这个方法负责把输入变成模型可读消息。

建议顺序：

1. system prompt
2. 历史摘要
3. 最近轮次问答
4. 当前问题

这里最重要的是顺序固定、上下文要裁剪。

#### 20.4.6 `answer()` 的实现说明

这个方法用于普通调用，适合先把链路跑通。

返回结构建议统一为：

```python
{
    "answer": "模型最终回答",
    "history": history,
}
```

这样 Service 层更容易接。

#### 20.4.7 `stream_answer()` 的实现说明

这个方法用于流式调用。

实现思路是：

1. 先发 `start`
2. 再逐段发 `chunk`
3. 最后发 `end`
4. 出错时发 `error`

这里要注意：流式输出不要改动核心业务逻辑，只是改变输出方式。

---

### 20.5 与当前项目的联动示例

Agent 在当前项目中通常被 `game_service` 调用。

```python
result = await guess_agent.answer(
    question=question,
    history=history,
    mode="agent",
)
```

如果是小助手调用：

```python
result = await guess_agent.answer(
    question=question,
    history=history,
    mode="helper",
)
```

如果需要流式：

```python
async for event in guess_agent.stream_answer(
    question=question,
    history=history,
    mode="agent",
):
    pass
```

---

### 20.6 典型实现顺序

建议你按下面顺序真正写代码：

1. 先写 `PromptLoader`
2. 再写 `MemoryPolicy`
3. 再写 `streaming.py`
4. 再写 `GuessAgent.__init__()`
5. 再写 `_build_agent_model()` 和 `_build_helper_model()`
6. 再写 `_load_prompt()`
7. 再写 `_build_messages()`
8. 再写 `answer()`
9. 最后写 `stream_answer()`

这样能保证你是逐步验证，而不是一次性堆完再排错。

---

## 21. 代码实现注意事项

### 21.1 不要在 Agent 中写数据库逻辑

Agent 的职责是模型调用，不是存储。

### 21.2 不要把所有历史直接塞给模型

上下文必须裁剪，否则模型容易变慢、变乱、忘前文。

### 21.3 不要把主模型和小助手混成一套 prompt

两者职责不同，策略应该分离。

### 21.4 不要先做复杂链

先把普通回答跑通，再做流式，再做摘要。

### 21.5 不要让一个方法干太多事

每个方法都尽量只负责一个职责，这样后续更好维护。

---

## 22. 结论

如果你按照本文件的方式去写，Agent 层会比较清晰：

- prompt 文件化
- 记忆按 game_id 隔离
- 主模型和小助手分离
- 普通调用与流式调用并存
- Service 层负责流程，Agent 层负责推理

这就是当前项目里最适合落地的 Agent 代码实现方式。
