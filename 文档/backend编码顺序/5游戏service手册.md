# 5 游戏 Service 手册

## 1. 文档目标

这一章的目标是指导你完成后端的游戏 Service 层，也就是把 API 层、Agent 层、Repository 层和 MongoDB 串起来的业务编排模块。

写完这一章后，你应该能够明确下面这些事情：

- Service 层在整个后端架构中的位置
- 游戏一局的完整生命周期应该怎么走
- 什么时候调用 Agent，什么时候写数据库，什么时候更新状态
- 普通返回和流式返回分别怎么组织
- Service 层应该保存哪些业务规则，哪些逻辑应该下沉到其他层

这一章的重点不是“怎么调用模型”，而是“怎么把一局游戏稳定地跑起来”。

---

## 2. Service 层在架构中的位置

在当前项目里，推荐把后端分成四层：

```text
API 层 -> Service 层 -> Agent 层 -> Repository 层 -> MongoDB
```

### 2.1 API 层负责什么

API 层只负责：

- 接收请求参数
- 做最基础的参数校验
- 调用 Service 层
- 把 Service 层返回的数据转换成 HTTP 响应

### 2.2 Service 层负责什么

Service 层负责真正的业务流程编排：

- 创建游戏
- 读取游戏状态
- 读取历史回合
- 调用 Agent 生成回答
- 把新回合写回数据库
- 更新游戏状态
- 组织返回结果

### 2.3 Agent 层负责什么

Agent 层只负责模型交互：

- 读取 prompt
- 组装消息
- 调用主模型或小助手模型
- 处理流式输出
- 生成答案文本

### 2.4 Repository 层负责什么

Repository 层只负责数据库访问：

- 创建记录
- 查询记录
- 更新记录
- 追加历史
- 写入摘要

Service 层不要直接操作原始 MongoDB 连接，应该通过 Repository 接口来做持久化。

---

## 3. 为什么要单独写游戏 Service

如果没有 Service 层，API 层会变得很重，Agent 层也会被数据库细节污染，最后整个项目会变成“路由里写业务、业务里写查询、查询里写模型调用”的混乱结构。

单独写游戏 Service 的好处是：

- 路由更薄，后续更容易维护
- 游戏状态集中管理，不容易串逻辑
- Agent 和数据库解耦，方便以后替换
- 后续如果要加房间、积分、排行榜，也能在 Service 层扩展

对这个项目来说，Service 层是“游戏流程控制中心”。

---

## 4. 这一章要解决的核心问题

### 4.1 为什么不能让 API 直接调 Agent

如果 API 直接调 Agent，会出现这些问题：

- 请求校验、状态检查、数据库写入全挤在一起
- 后续改流程时要改多个路由文件
- 流式输出和普通输出难以统一
- 失败重试和异常处理很难收口

### 4.2 为什么不能让 Agent 直接写数据库

Agent 的职责是推理，不是持久化。

如果 Agent 直接写数据库，会导致：

- 模型逻辑和存储逻辑耦合
- 难以测试
- 复用困难
- 后续迁移存储时风险很高

### 4.3 为什么不能让 Repository 直接控制业务

Repository 只知道“存什么、取什么”，不知道“为什么存、什么时候存、存完以后该做什么”。

业务判断应该留在 Service 层。

---

## 5. 建议目录结构

建议把游戏 Service 相关代码放在下面这个结构中：

```text
backend/
└── app/
    ├── services/
    │   └── game_service.py
    ├── repositories/
    │   └── game_repo.py
    └── agents/
        ├── guess_agent.py
        └── utils/
            ├── memory_policy.py
            ├── prompt_loader.py
            └── streaming.py
```

如果后续还要拆分，可以继续加这些文件：

- `game_state_service.py`：专门处理状态流转
- `game_history_service.py`：专门处理历史回合
- `game_result_service.py`：专门处理胜负和结算

当前 demo 阶段不建议拆太细，先用一个 `GameService` 把主流程跑通就够了。

---

## 6. GameService 的职责边界

### 6.1 GameService 应该做的事情

GameService 应该负责下面这些事情：

- 创建游戏记录
- 检查游戏是否存在
- 检查游戏是否已经结束
- 读取历史回合
- 调用 Agent 获取答案
- 保存本轮问答
- 更新游戏状态
- 组织普通响应和流式响应

### 6.2 GameService 不应该做的事情

GameService 不应该直接承担下面这些职责：

- 不直接处理 HTTP 协议细节
- 不直接拼接 prompt
- 不直接控制模型参数
- 不直接操作底层 MongoDB 客户端
- 不直接承担前端展示逻辑

### 6.3 这一层的核心原则

一句话概括：

**Service 层负责“流程正确”，Agent 层负责“回答正确”，Repository 层负责“数据正确”。**

---

## 7. 游戏数据结构建议

为了让 Service 层和 Agent 层配合稳定，建议把游戏记录设计成下面这种结构。

### 7.1 游戏主记录

建议一个游戏记录至少包含这些字段：

- `game_id`：游戏唯一标识
- `status`：游戏状态，比如 `pending`、`active`、`finished`
- `history`：历史回合列表
- `summary`：历史摘要
- `round_count`：已进行轮次
- `created_at`：创建时间
- `updated_at`：更新时间
- `finished_at`：结束时间，可选
- `metadata`：扩展信息，可选

### 7.2 单轮记录

每一轮历史建议至少包含：

- `round_no`：第几轮
- `question`：用户问题
- `answer`：Agent 回答
- `mode`：调用模式，比如 `agent` 或 `helper`
- `created_at`：回合时间
- `latency_ms`：响应耗时，可选
- `error`：异常信息，可选

### 7.3 为什么要保留 history

`history` 的作用不是为了每次都完整喂给模型，而是为了：

- 还原游戏过程
- 方便调试
- 方便做摘要压缩
- 方便后续统计和回放

### 7.4 为什么还要保留 summary

当历史越来越长时，模型不适合接收全部对话。

`summary` 用来保留更早轮次的关键信息，避免上下文无限增长。

---

## 8. GameService 的核心方法设计

这一章建议先把 GameService 设计成一个负责“整局游戏生命周期”的类。

### 8.1 初始化方法

初始化阶段建议注入这些对象：

- `settings`：配置对象
- `agent`：猜词 Agent
- `repository`：游戏仓储
- `memory_policy`：记忆策略

这样设计的好处是：

- 依赖关系清晰
- 方便单元测试
- 方便替换实现
- 方便在不同环境下切换模型或存储策略

### 8.2 创建游戏

创建游戏的方法建议负责：

- 生成 `game_id`
- 初始化游戏状态
- 写入 MongoDB
- 返回可供前端使用的基础信息

这个方法的关键点是：

- 不要一上来就调用 Agent
- 不要把业务问题和答案混在创建逻辑里
- 只做“开局”动作

### 8.3 获取游戏详情

获取游戏详情的方法建议负责：

- 按 `game_id` 查记录
- 返回当前状态
- 返回历史回合
- 返回摘要信息

这个方法通常不会调用模型，只做读取。

### 8.4 提交一轮问答

这是 Service 层最重要的方法之一。

它通常负责：

- 校验游戏是否存在
- 校验游戏是否还能继续
- 读取历史回合
- 调用 Agent 生成回答
- 把新回合追加到历史中
- 更新轮次和更新时间
- 返回最终结果

### 8.5 流式提交问答

如果前端需要逐段显示答案，就需要流式版本。

流式方法通常负责：

- 先检查游戏状态
- 再读取历史
- 再调用 Agent 的流式接口
- 一边向前端吐事件，一边缓存最终答案
- 结束后统一写库

### 8.6 结束游戏

结束游戏的方法建议负责：

- 修改状态为 `finished`
- 记录结束时间
- 记录结束原因
- 保留完整历史

---

## 9. 推荐的业务流程

这一部分是整章最重要的实现顺序。

### 9.1 创建游戏流程

推荐流程如下：

1. API 收到创建请求
2. API 调用 `GameService.create_game()`
3. Service 生成 `game_id`
4. Service 通过 Repository 写入初始记录
5. Service 返回创建结果

这里的关键是先把游戏状态建起来，再开始后续猜词。

### 9.2 普通问答流程

推荐流程如下：

1. API 收到当前轮问题
2. API 调用 `GameService.submit_turn()`
3. Service 读取游戏记录
4. Service 判断游戏是否可继续
5. Service 取出历史回合
6. Service 调用 Agent 生成回答
7. Service 追加当前轮历史
8. Service 更新数据库
9. Service 返回结果

### 9.3 流式问答流程

推荐流程如下：

1. API 收到流式请求
2. API 调用 `GameService.submit_turn_stream()`
3. Service 做前置校验
4. Service 调用 Agent 的流式方法
5. Service 把 `start`、`chunk`、`end` 事件转发给前端
6. 生成完成后统一写回数据库

### 9.4 结束流程

推荐流程如下：

1. API 调用 `GameService.end_game()`
2. Service 更新状态
3. Service 写入结束时间
4. Service 返回结束结果

---

## 10. 参考实现结构

这一部分给你一个建议中的类结构。你可以把它当成实现时的骨架，而不是直接照搬的最终代码。

```python
class GameService:
    def __init__(self, settings, agent, repository, memory_policy):
        self.settings = settings
        self.agent = agent
        self.repository = repository
        self.memory_policy = memory_policy

    async def create_game(self, owner_id=None):
        ...

    async def get_game(self, game_id: str):
        ...

    async def submit_turn(self, game_id: str, question: str, mode: str = "agent"):
        ...

    async def submit_turn_stream(self, game_id: str, question: str, mode: str = "agent"):
        ...

    async def end_game(self, game_id: str, reason: str = "manual"):
        ...
```

### 10.1 create_game 的参考职责

这个方法建议完成：

- 生成唯一 ID
- 初始化默认状态
- 初始化空历史
- 写入数据库
- 返回创建结果

### 10.2 get_game 的参考职责

这个方法建议完成：

- 查询游戏记录
- 判断是否存在
- 返回完整文档或视图对象

### 10.3 submit_turn 的参考职责

这个方法建议完成：

- 读取游戏记录
- 校验状态
- 读取历史
- 交给 Agent 生成答案
- 把结果写回 history
- 更新 summary 或轮次

### 10.4 submit_turn_stream 的参考职责

这个方法建议完成：

- 读取游戏记录
- 调用 Agent 流式接口
- 逐段返回事件
- 在最后保存完整结果

### 10.5 end_game 的参考职责

这个方法建议完成：

- 把状态切到结束
- 记录结束原因
- 记录结束时间

---

## 11. 详细实现思路

### 11.1 先查状态，再做调用

在调用 Agent 之前，Service 一定要先检查游戏状态。

如果游戏已经结束，就不要继续生成回答。

这样做可以避免：

- 结束游戏后还能继续发问
- 历史状态被错误追加
- 数据库里出现矛盾记录

### 11.2 先读历史，再交给 Agent

Agent 不应该自己去数据库找历史。

Service 层应该先拿到完整历史，再把历史传给 Agent。

这样做的好处是：

- Agent 更纯粹
- 历史读取逻辑统一
- 后续更容易测试

### 11.3 先拿到模型结果，再写回数据库

正常情况下，推荐顺序是：

1. 让 Agent 生成回答
2. 拿到最终答案
3. 再把答案写入历史

不要反过来先写半成品再等模型返回，否则失败时会留下脏数据。

### 11.4 流式场景要缓存最终结果

流式输出时，前端会先看到一段一段的内容。

但数据库里最终应该保存一条完整回答。

所以流式过程中建议：

- 一边转发 chunk
- 一边在 Service 内部缓存完整文本
- 结束后再一次性写入数据库

这样最稳。

---

## 12. 参考代码说明

下面这段是更接近实际实现的参考写法。你可以在真正动手写代码时，按照这个方向展开。

```python
class GameService:
    async def submit_turn(self, game_id: str, question: str, mode: str = "agent"):
        game = await self.repository.get_game(game_id)
        if not game:
            raise ValueError("Game not found")

        if game.get("status") == "finished":
            raise ValueError("Game already finished")

        history = game.get("history", [])
        result = await self.agent.answer(question=question, history=history, mode=mode)

        answer = result["answer"]
        updated_history = result["history"]

        await self.repository.update_game_history(
            game_id=game_id,
            history=updated_history,
            summary=self.memory_policy.build_summary(updated_history),
            round_count=len(updated_history),
        )

        return {
            "game_id": game_id,
            "question": question,
            "answer": answer,
            "history": updated_history,
        }
```

这段参考逻辑体现了一个重要原则：

- Agent 负责产出结果
- Service 负责收口结果并持久化

### 12.1 为什么要在 Service 里更新 summary

因为 summary 属于“当前游戏状态的一部分”，不是 Agent 的临时输出。

把 summary 写回数据库后，后续读取游戏时就能更快构造上下文。

### 12.2 为什么要更新 round_count

轮次是最基础的状态指标。

它可以用于：

- 限制最大轮次
- 统计游戏进度
- 决定是否需要摘要压缩

---

## 13. 异常处理建议

Service 层一定要有明确的异常处理策略。

### 13.1 常见异常

常见异常包括：

- 游戏不存在
- 游戏已经结束
- 问题为空
- Agent 调用失败
- 数据库写入失败

### 13.2 推荐处理方式

推荐做法是：

- 业务异常交给 Service 抛出明确错误
- API 层把错误转换成合适的 HTTP 响应
- Agent 内部异常不要直接吞掉，要保留可排查信息

### 13.3 流式异常处理

流式场景下如果 Agent 报错，建议：

- 先发一个 `error` 事件
- 再发一个结束事件
- 不要把半成品答案写进正式 history

---

## 14. 与记忆策略的关系

这一章和上一章的 `MemoryPolicy` 是直接联动的。

### 14.1 Service 层应该如何使用记忆策略

有两种常见方式：

1. 由 Agent 内部处理记忆截断和摘要
2. 由 Service 层在保存时同步更新 summary

对于当前 demo，推荐优先使用第二种的最小实现：

- Agent 负责生成答案
- Service 负责保存 history 和 summary

### 14.2 为什么 summary 适合放在数据库里

因为它属于游戏状态的一部分。

这样后续重新加载游戏时，不需要重新扫描所有历史就能快速恢复上下文。

---

## 15. 调试顺序建议

建议按下面顺序调试这一层：

1. 先把创建游戏跑通
2. 再把单轮普通问答跑通
3. 再验证历史是否正确写入 MongoDB
4. 再测结束状态
5. 最后再测流式输出

### 15.1 先验证创建游戏

先确认数据库里能出现一条新的游戏记录。

### 15.2 再验证单轮问答

确认每次提问后，历史数组能正确增长，答案也能正确落库。

### 15.3 再验证流式输出

确认前端能持续收到 chunk，并且结束后数据库里保存的是完整结果。

---

## 16. 本章的实现优先级

如果你要按章节推进，建议这个顺序：

1. 先实现 `game_service.py` 的最小骨架
2. 再补 `game_repo.py` 的基础查询和写入
3. 再把 Agent 调用接入 Service
4. 再补流式接口
5. 最后再加状态判断和结算逻辑

这个顺序的好处是：

- 最先跑通主链路
- 方便逐步验证
- 不会一开始就陷入复杂边界条件

---

## 17. 与上一章和下一章的衔接

### 17.1 与上一章的衔接

上一章已经把 Agent 调用类讲清楚了，Service 层在这里要做的事情很简单：

- 把历史和问题传给 Agent
- 接收 Agent 的结果
- 把结果写回数据库

也就是说，Service 是 Agent 的外层编排者。

### 17.2 与下一章的衔接

下一章建议继续写 Repository 手册，因为 Service 最终要依赖 Repository 完成持久化。

如果 Repository 层没有先定义清楚，Service 的实现会很容易反复改动。

---

## 18. 本章结论

Game Service 是这一套后端里最重要的流程层之一。

它不负责模型推理本身，也不负责数据库细节本身，它负责的是：

- 把业务顺序理顺
- 把状态流转管住
- 把 Agent 和存储串起来
- 把普通调用和流式调用统一起来

如果这一层写得清楚，后面的 Repository、接口层、甚至未来的房间和排行榜功能都会很好扩展。

---

## 19. GameService 详细代码实现参考

这一节把 `game_service.py` 的每个方法都拆开说明，目标是让你可以按方法逐个实现，而不是把整层逻辑一次性堆进去。

### 19.1 `__init__()` 的实现

`GameService` 的初始化不应该做业务逻辑，只负责接收依赖并保存下来。

建议注入四个对象：

- `settings`：配置对象，提供最大轮次、超时、模型参数等
- `agent`：`GuessAgent` 实例，负责模型调用
- `repository`：`GameRepository` 实例，负责数据库读写
- `memory_policy`：`MemoryPolicy` 实例，负责历史压缩和摘要

初始化阶段的重点是依赖注入，而不是创建业务状态。

#### 参考实现思路

```python
class GameService:
    def __init__(self, settings, agent, repository, memory_policy):
        self.settings = settings
        self.agent = agent
        self.repository = repository
        self.memory_policy = memory_policy
```

#### 设计考虑

- 这样做以后方便单元测试，可以直接注入 mock 对象
- 这样做以后方便替换 Agent 或 Repository 的实现
- 这样做以后 Service 层不会和具体配置文件强绑定

---

### 19.2 `create_game()` 的实现

这个方法负责创建一局新的游戏。

它的职责不是“开始模型推理”，而是“初始化一局游戏的数据状态”。

#### 推荐执行步骤

1. 生成新的 `game_id`
2. 计算初始时间戳
3. 组装默认游戏记录
4. 调用 Repository 写入数据库
5. 返回创建结果

#### 需要初始化的字段

建议至少包括：

- `game_id`
- `status`，初始值可以是 `active` 或 `pending`
- `history`，初始为空数组
- `summary`，初始为空字符串
- `round_count`，初始为 `0`
- `created_at`
- `updated_at`
- `finished_at`，初始为空
- `metadata`，可选扩展字段

#### 推荐实现思路

```python
async def create_game(self, owner_id=None):
    game_id = ...
    now = ...

    game_doc = {
        "game_id": game_id,
        "status": "active",
        "history": [],
        "summary": "",
        "round_count": 0,
        "owner_id": owner_id,
        "created_at": now,
        "updated_at": now,
        "finished_at": None,
        "metadata": {},
    }

    await self.repository.create_game(game_doc)

    return {
        "game_id": game_id,
        "status": "active",
        "round_count": 0,
        "created_at": now,
    }
```

#### 设计考虑

- 创建游戏时不要预先调用 Agent
- 创建游戏时不要把历史塞进去
- 创建游戏时只做初始化，避免和提问流程耦合

#### 常见错误

- 直接把“首轮问题”塞进创建逻辑
- 创建游戏时忘记设置 `updated_at`
- 创建游戏时没有返回 `game_id`

---

### 19.3 `get_game()` 的实现

这个方法负责按 `game_id` 查询一局游戏的完整数据。

它通常是一个纯读取方法，不应该修改数据库状态。

#### 推荐执行步骤

1. 调用 Repository 查询游戏
2. 判断是否存在
3. 判断是否需要过滤敏感字段
4. 返回完整文档或视图对象

#### 推荐实现思路

```python
async def get_game(self, game_id: str):
    game = await self.repository.get_game(game_id)
    if not game:
        raise ValueError(f"Game with id {game_id} not found")
    return game
```

#### 设计考虑

- 如果项目还没有权限体系，可以先返回完整记录
- 如果后续有前端展示需要，可以再增加视图层转换
- 如果后续要隐藏内部字段，可以在 Service 层统一裁剪

#### 常见错误

- 直接把 `None` 返回给上层，导致 API 层不清楚怎么处理
- 查询后忘记做存在性判断
- 读取方法里顺手改了数据库状态

---

### 19.4 `submit_turn()` 的实现

这个方法是当前 Service 层最关键的普通请求入口。

它的任务是：

- 检查游戏状态
- 读取历史
- 调用 Agent
- 保存新回合
- 返回答案和更新后的历史

#### 推荐执行步骤

1. 查询游戏记录
2. 判断游戏是否存在
3. 判断游戏是否已经结束
4. 读取历史回合
5. 把历史和当前问题交给 Agent
6. 接收 Agent 返回的答案和更新后的 history
7. 用 MemoryPolicy 重新生成摘要
8. 调用 Repository 更新游戏记录
9. 返回当前轮的结果

#### 推荐实现思路

```python
async def submit_turn(self, game_id: str, question: str, mode: str = "agent"):
    game = await self.repository.get_game(game_id)
    if not game:
        raise ValueError(f"Game with id {game_id} not found")

    if game.get("status") == "finished":
        raise ValueError(f"Game with id {game_id} has already finished")

    history = game.get("history", [])
    result = await self.agent.answer(question, history, mode)
    updated_history = result["history"]

    await self.repository.update_game_history(
        game_id,
        history=updated_history,
        summary=self.memory_policy.build_summary(updated_history),
        round_count=len(updated_history),
    )

    return {
        "game_id": game_id,
        "question": question,
        "answer": result["answer"],
        "history": updated_history,
    }
```

#### 设计考虑

- 先查游戏是否存在，再调用 Agent，避免无效请求浪费模型额度
- 先判断是否已结束，避免结束后的非法提问
- 让 Agent 返回更新后的 history，可以减少 Service 层自己拼接历史的复杂度
- 把摘要更新留在 Service 层，保证数据库中的上下文状态同步

#### 这里为什么要重算 summary

因为每次新回合写入后，摘要都可能变化。

如果不重算 summary，后续读取游戏时，模型看到的上下文就可能落后于实际历史。

#### 常见错误

- 调用 Agent 后没有把历史写回数据库
- 直接把 Agent 的返回字符串当成完整结果，忘了更新历史
- `round_count` 仍然停留在旧值
- `summary` 没有同步更新

---

### 19.5 `submit_turn_stream()` 的实现

这个方法负责流式版本的单轮提交。

它和普通版本的差别在于：不是一次性拿到完整答案，而是一边生成、一边向前端发事件。

#### 推荐执行步骤

1. 查询游戏记录
2. 判断游戏状态
3. 读取历史回合
4. 调用 Agent 的流式生成接口
5. 先发出 `start` 事件
6. 持续转发 `chunk` 事件
7. 在内部缓存完整回答
8. 生成结束后写入数据库
9. 发出 `end` 事件

#### 推荐实现思路

```python
async def submit_turn_stream(self, game_id: str, question: str, mode: str = "agent"):
    game = await self.repository.get_game(game_id)
    if not game:
        raise ValueError(f"Game with id {game_id} not found")

    if game.get("status") == "finished":
        raise ValueError(f"Game with id {game_id} has already finished")

    history = game.get("history", [])
    full_answer = ""

    yield build_stream_start()

    try:
        async for event in self.agent.stream_answer(question, history, mode):
            if event.get("type") == "chunk":
                full_answer += event.get("content", "")
            yield event

        updated_history = history + [{"question": question, "answer": full_answer}]
        await self.repository.update_game_history(
            game_id,
            history=updated_history,
            summary=self.memory_policy.build_summary(updated_history),
            round_count=len(updated_history),
        )

        yield build_stream_end()
    except Exception as exc:
        yield build_stream_error("Sorry, I encountered an error while processing your request.")
        raise exc
```

#### 设计考虑

- 流式方法里必须缓存完整答案，否则最后没法写回数据库
- 事件流和数据库写入要分开处理，避免半成品数据落库
- 如果 Agent 报错，要让前端收到错误事件

#### 常见错误

- 只转发 chunk，不保存 full_answer
- 结束后没有把完整结果写回 MongoDB
- 流式异常时直接中断，前端拿不到错误信息

---

### 19.6 `end_game()` 的实现

这个方法负责结束一局游戏。

它应该只做状态收口，不应该再调用 Agent。

#### 推荐执行步骤

1. 查询游戏是否存在
2. 判断是否已经结束
3. 更新状态为 `finished`
4. 写入结束原因
5. 写入结束时间
6. 返回结束结果

#### 推荐实现思路

```python
async def end_game(self, game_id: str, reason: str = "manual"):
    game = await self.repository.get_game(game_id)
    if not game:
        raise ValueError(f"Game with id {game_id} not found")

    if game.get("status") == "finished":
        return game

    now = ...
    await self.repository.finish_game(
        game_id,
        reason=reason,
        finished_at=now,
    )

    return {
        "game_id": game_id,
        "status": "finished",
        "reason": reason,
        "finished_at": now,
    }
```

#### 设计考虑

- 结束游戏后应当禁止继续提问
- 结束时要保留完整历史，便于回放和调试
- 如果重复结束，可以直接返回当前状态，不必报错太重

#### 常见错误

- 只改状态没写结束时间
- 结束时把历史清空
- 结束后还能继续 submit_turn

---

### 19.7 建议补充的内部辅助方法

如果你希望 `game_service.py` 更整洁，可以额外拆出几个内部辅助方法。

#### `_require_game()`

用于统一处理“游戏不存在”的检查。

#### `_require_active_game()`

用于统一处理“游戏已结束”的检查。

#### `_build_turn_record()`

用于统一构造单轮问答记录。

#### `_refresh_summary()`

用于统一更新摘要内容，避免在多个方法里重复写摘要逻辑。

这些辅助方法不是必须，但如果后面 Service 逻辑继续增长，它们会明显提高可读性。

---

## 20. 本章补充结论

如果你按照上面的方式实现 `game_service.py`，这一层的代码会比较稳定：

- `create_game()` 负责开局
- `get_game()` 负责读取
- `submit_turn()` 负责普通回合
- `submit_turn_stream()` 负责流式回合
- `end_game()` 负责收口

这样的拆分方式可以确保业务边界清晰，也能让下一章 Repository 手册更容易落地。
