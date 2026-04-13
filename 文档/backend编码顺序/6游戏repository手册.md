# 6 游戏 Repository 手册

## 1. 文档目标

这一章的目标是指导你完成后端的游戏 Repository 层，也就是把游戏数据真正写入 MongoDB、读出 MongoDB、更新 MongoDB 的那一层。

写完这一章后，你应该能够明确下面这些事情：

- Repository 层在整个后端架构中的位置
- 游戏数据应该存在哪个集合里
- Repository 层应该提供哪些方法
- 如何把创建、查询、更新、结束游戏拆成稳定的数据访问接口
- 如何保证 Service 层调用 Repository 时结构清晰、职责单一

这一章的重点不是业务判断，而是“如何把游戏状态正确、安全地落到数据库里”。

---

## 2. Repository 层在架构中的位置

在当前项目里，Repository 层位于 Service 层和 MongoDB 之间：

```text
API 层 -> Service 层 -> Repository 层 -> MongoDB
```

### 2.1 Repository 层负责什么

Repository 层负责所有数据访问相关操作：

- 创建游戏记录
- 按 `game_id` 查询游戏
- 按条件查询游戏列表
- 更新游戏历史
- 更新游戏状态
- 写入结束时间和结束原因
- 维护索引和数据一致性

### 2.2 Repository 层不负责什么

Repository 层不应该直接负责这些事情：

- 不判断游戏是否应该继续
- 不决定 Agent 应该怎么回答
- 不拼接 prompt
- 不处理前端请求
- 不做复杂业务编排

Repository 只关心“数据怎么存、怎么取、怎么更新”。

---

## 3. 为什么要单独写 Repository

如果没有 Repository 层，Service 层就会直接操作 MongoDB，最后会变成：

- 业务逻辑和数据库语句混在一起
- 未来替换存储时要改很多地方
- 测试难度上升
- 同样的更新逻辑容易在多个地方重复出现

单独写 Repository 的好处是：

- 数据访问统一
- 查询和更新逻辑可复用
- Service 层更干净
- 后续增加缓存、审计、归档更容易

对这个项目来说，Repository 层是“游戏数据的唯一入口”。

---

## 4. 游戏集合建议

### 4.1 集合名称

建议把游戏主集合命名为：

- `games`

这个命名简单、明确，也适合后续扩展。

### 4.2 为什么只需要一个主集合

当前 demo 阶段建议先把一局游戏的主记录完整放在一个集合里，包含：

- 游戏基础信息
- 当前状态
- 历史回合
- 摘要信息
- 结束状态

这样做的好处是：

- 实现简单
- 读取方便
- 一局游戏的数据天然聚合在一起

后续如果数据量变大，再考虑拆成：

- `games`
- `game_turns`
- `game_snapshots`

但当前阶段不建议过早拆分。

---

## 5. 游戏文档建议结构

Repository 里存的游戏文档建议包含这些字段：

- `game_id`：游戏唯一标识
- `owner_id`：创建者或所属用户，可选
- `status`：`pending`、`active`、`finished`
- `history`：回合数组
- `summary`：历史摘要
- `round_count`：回合数
- `created_at`：创建时间
- `updated_at`：更新时间
- `finished_at`：结束时间，可选
- `finish_reason`：结束原因，可选
- `metadata`：扩展信息，可选

### 5.1 history 字段建议

`history` 中每一轮建议是一个字典，至少包含：

- `question`
- `answer`
- `mode`
- `created_at`

如果后续要做统计，可以继续加：

- `latency_ms`
- `error`
- `round_no`

### 5.2 为什么要把 summary 存在主文档里

因为 summary 是当前游戏上下文的一部分，不是临时计算结果。

把它一起保存后，Service 层读取游戏时就能更快恢复上下文。

---

## 6. 索引建议

Repository 层最好在初始化阶段确保索引存在。

### 6.1 必要索引

建议至少创建这些索引：

- `game_id` 唯一索引
- `status` 普通索引
- `owner_id` 普通索引，可选
- `updated_at` 普通索引，可选

### 6.2 索引的作用

索引的作用主要是：

- 保证 `game_id` 唯一
- 提高按主键查询速度
- 提高按状态或用户筛选的速度

### 6.3 为什么要提前建索引

如果不提前建索引，后面数据量变大后，查询和去重都会变慢。

尤其是 `game_id`，必须保证唯一，否则会出现同一局游戏被重复创建的风险。

---

## 7. Repository 的职责边界

### 7.1 Repository 应该做的事情

Repository 应该负责这些事情：

- 插入游戏记录
- 查询游戏记录
- 更新历史回合
- 更新摘要和轮次
- 修改状态
- 结束游戏

### 7.2 Repository 不应该做的事情

Repository 不应该负责：

- 判断游戏是否已经结束
- 判断用户输入是否合法
- 调用 Agent
- 拼接 prompt
- 决定返回给前端什么结构

### 7.3 核心原则

一句话概括：

**Repository 负责“数据库操作正确”，Service 负责“业务流程正确”。**

---

## 8. 推荐的类结构

建议把 Repository 设计成一个专门管理 `games` 集合的类。

### 8.1 初始化阶段

初始化阶段建议接收：

- `db`：MongoDB 数据库对象

然后在内部固定集合名：

- `self.collection = db["games"]`

### 8.2 推荐职责

这个类建议提供以下能力：

- `create_game()`
- `get_game()`
- `update_game_history()`
- `finish_game()`
- `list_games()`，可选

如果后面需要更细，还可以加：

- `update_summary()`
- `update_status()`
- `delete_game()`

当前 demo 阶段先把主流程方法实现清楚就够了。

---

## 9. 方法级详细实现参考

这一节把 Repository 的核心方法逐个拆开说明。

### 9.1 `__init__()` 的实现

Repository 初始化只做两件事：

1. 保存数据库对象
2. 获取集合引用

#### 参考实现思路

```python
class GameRepository:
    def __init__(self, db):
        self.db = db
        self.collection = db["games"]
```

#### 设计考虑

- 这样写以后，所有游戏数据操作都集中到同一个集合
- Service 层只需要传入 Repository，不需要知道集合细节
- 后续如果集合名改动，只改 Repository 内部即可

---

### 9.2 `create_game()` 的实现

这个方法负责把一局新的游戏写入数据库。

#### 推荐执行步骤

1. 检查待插入文档是否包含 `game_id`
2. 确保 `game_id` 没有重复
3. 插入游戏主文档
4. 返回插入结果

#### 推荐实现思路

```python
async def create_game(self, game_doc: dict):
    await self.collection.insert_one(game_doc)
    return game_doc
```

#### 更稳妥的做法

实际实现时，可以先检查是否已经存在相同 `game_id`：

```python
existing = await self.collection.find_one({"game_id": game_doc["game_id"]})
if existing:
    raise ValueError("game_id already exists")
```

#### 设计考虑

- 创建时应该保证 `game_id` 唯一
- 创建时不要自动改写业务状态
- 创建时不要混入 Agent 调用结果

#### 常见错误

- 忘记唯一性检查
- 插入字段不完整
- 创建时没有返回插入后的主键或游戏 ID

---

### 9.3 `get_game()` 的实现

这个方法负责按 `game_id` 查询单局游戏。

#### 推荐执行步骤

1. 使用 `game_id` 查询文档
2. 如果不存在则返回 `None`
3. 如果存在则返回完整文档

#### 推荐实现思路

```python
async def get_game(self, game_id: str):
    return await self.collection.find_one({"game_id": game_id})
```

#### 设计考虑

- 这个方法应保持纯查询语义
- 不要在查询时顺便修改状态
- 不要在这里做业务判断

#### 常见错误

- 查询条件写错
- 忘记按 `game_id` 精确查询
- 返回的是游标而不是单条文档

---

### 9.4 `update_game_history()` 的实现

这个方法负责在一轮问答完成后，更新游戏历史、摘要、轮次和更新时间。

这是 Repository 层最重要的更新方法之一。

#### 推荐执行步骤

1. 按 `game_id` 找到目标文档
2. 更新 `history`
3. 更新 `summary`
4. 更新 `round_count`
5. 更新 `updated_at`
6. 返回更新结果

#### 推荐实现思路

```python
async def update_game_history(self, game_id: str, history: list[dict], summary: str, round_count: int):
    result = await self.collection.update_one(
        {"game_id": game_id},
        {
            "$set": {
                "history": history,
                "summary": summary,
                "round_count": round_count,
                "updated_at": datetime.now(),
            }
        },
    )
    return result
```

#### 设计考虑

- 更新历史后一定要同步更新摘要
- 更新历史后一定要同步更新轮次
- 更新历史后一定要刷新更新时间

#### 为什么这里建议一次性更新多个字段

因为这些字段是同一个业务动作的一部分。

如果拆成多个更新步骤，中间一旦失败，就容易出现：

- history 已更新但 summary 没更新
- round_count 已更新但 updated_at 没更新

所以建议尽量一次性完成。

#### 常见错误

- 只更新 history，忘记更新 summary
- 只更新 summary，忘记更新 round_count
- `updated_at` 使用错误的时间源

---

### 9.5 `finish_game()` 的实现

这个方法负责把游戏状态切换成结束状态，并写入结束时间和结束原因。

#### 推荐执行步骤

1. 按 `game_id` 查找文档
2. 将 `status` 更新为 `finished`
3. 写入 `finished_at`
4. 写入 `finish_reason`
5. 更新 `updated_at`
6. 返回更新结果

#### 推荐实现思路

```python
async def finish_game(self, game_id: str, reason: str, finished_at):
    result = await self.collection.update_one(
        {"game_id": game_id},
        {
            "$set": {
                "status": "finished",
                "finish_reason": reason,
                "finished_at": finished_at,
                "updated_at": datetime.now(),
            }
        },
    )
    return result
```

#### 设计考虑

- 结束游戏时要保留历史，不能清空
- 结束游戏时要记录原因，方便后续调试和统计
- 结束游戏时也要更新 `updated_at`

#### 常见错误

- 只改 `status`，没有记录结束时间
- 结束时把历史覆盖掉
- 没有检查目标游戏是否存在

---

### 9.6 `list_games()` 的实现

这个方法不是当前主流程必须的，但后续很有用。

它适合做：

- 游戏列表页
- 管理后台
- 调试和统计

#### 推荐执行步骤

1. 根据筛选条件构建查询
2. 设置排序和分页
3. 返回结果列表

#### 推荐实现思路

```python
async def list_games(self, filter_query: dict | None = None, limit: int = 20, skip: int = 0):
    query = filter_query or {}
    cursor = self.collection.find(query).sort("updated_at", -1).skip(skip).limit(limit)
    return await cursor.to_list(length=limit)
```

#### 设计考虑

- 排序默认按最近更新时间倒序
- 列表接口通常要支持分页
- 列表接口可以只返回摘要字段，不一定返回完整 history

---

## 10. 与 GameService 的联动方式

这一章和上一章是直接配套的。

### 10.1 创建游戏时

GameService 会组装一个完整的 `game_doc`，然后调用：

- `repository.create_game(game_doc)`

### 10.2 查询游戏时

GameService 会调用：

- `repository.get_game(game_id)`

### 10.3 提交回合时

GameService 在拿到 Agent 的结果后，会调用：

- `repository.update_game_history(...)`

### 10.4 结束游戏时

GameService 会调用：

- `repository.finish_game(game_id, reason, finished_at)`

也就是说，Repository 本身不主动决定什么时候执行，只是接收来自 Service 层的明确指令。

---

## 11. 异常处理建议

Repository 层也需要有明确的异常策略。

### 11.1 常见异常

常见异常包括：

- 数据库连接失败
- 插入失败
- 更新失败
- 唯一索引冲突
- 文档不存在

### 11.2 推荐处理方式

建议 Repository 层尽量抛出明确异常，让 Service 层决定怎么处理。

例如：

- 找不到文档可以返回 `None`
- 唯一性冲突可以抛 `ValueError`
- 数据库底层异常可以继续向上抛出，交给统一异常处理层

### 11.3 为什么不要在 Repository 里吞异常

因为 Repository 是最接近数据源的地方，如果这里把异常吞掉，Service 层就会误以为操作成功。

这会导致数据状态和业务状态不一致。

---

## 12. 事务和一致性建议

MongoDB 在当前 demo 里可以先采用单文档更新的方式，这样足够稳定。

### 12.1 为什么单文档更新就够了

因为当前一局游戏的数据都放在一个主文档里，更新历史、摘要、轮次、状态时可以一次更新完成。

### 12.2 如果后续拆分多集合怎么办

如果以后拆成多个集合，就要重新考虑：

- 事务
- 幂等性
- 回滚
- 写入顺序

当前阶段不需要过度复杂化。

---

## 13. 调试顺序建议

建议按下面顺序调试 Repository 层：

1. 先确认 MongoDB 连接正常
2. 再确认能创建一条游戏记录
3. 再确认能按 `game_id` 读回记录
4. 再确认能更新 history 和 summary
5. 再确认能把状态改成 `finished`

### 13.1 先验证索引

先确认 `game_id` 唯一索引是否生效。

### 13.2 再验证创建和读取

创建后立刻读取，确认字段完整。

### 13.3 再验证更新

更新后检查 `history`、`summary`、`round_count`、`updated_at` 是否同步变化。

---

## 14. 推荐实现顺序

如果你准备开始写 `game_repo.py`，建议按这个顺序来：

1. 先写 `__init__()`
2. 再写 `create_game()`
3. 再写 `get_game()`
4. 再写 `update_game_history()`
5. 再写 `finish_game()`
6. 最后补 `list_games()`

这个顺序的好处是：

- 先把主链路跑通
- 后续方法可以直接复用前面的方法约定
- 不容易在一开始就陷入分页、筛选、统计等非核心问题

---

## 15. 本章结论

Repository 层是游戏数据的唯一入口，它负责把 `GameService` 的业务动作变成稳定的 MongoDB 操作。

如果这一层写得清楚，Service 层就会变得很干净，Agent 层也能继续保持纯推理职责。

当前这个项目里，Repository 的核心目标不是“写很多方法”，而是：

- 把游戏文档结构固定下来
- 把主流程方法定义清楚
- 把数据库更新做成单一、稳定、可测试的入口

只要这几件事做好，后面的接口层和 Agent 层都会更容易推进。
