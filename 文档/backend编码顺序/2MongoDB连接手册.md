# 2MongoDB连接手册

## 1. 文档目的

这一章的目标是指导你完成后端的 MongoDB 连接层。它的作用不是直接处理业务，而是把数据库连接这件事封装成一个稳定、可复用、易关闭的基础模块，供后续 Repository 层和 Service 层使用。

这一章完成后，你的后端应该具备以下能力：

- 能读取统一配置中的 MongoDB 地址和数据库名
- 能创建异步 MongoDB 客户端
- 能在应用启动时初始化连接
- 能在应用关闭时释放连接
- 能为后续集合创建基础索引
- 能让 Repository 层只关心数据操作，不关心连接细节

## 2. 这一章为什么要单独写

MongoDB 连接不是一个“顺手写一下”的模块，它属于后端基础设施层。

如果连接层不稳定，会直接影响：

- 游戏记录是否能保存
- 回合数据是否能追加
- 读取历史上下文是否可靠
- 后续接口能否稳定运行

所以建议你先把连接层做扎实，再继续写 Repository 和 Service。

## 3. MongoDB 连接层的职责边界

MongoDB 连接层只负责数据库连接相关事情：

- 创建 MongoDB 客户端
- 获取数据库对象
- 在启动时做初始化
- 在关闭时释放资源
- 创建必要索引

它不应该负责：

- 业务逻辑判断
- 数据结构转换
- 具体增删改查方法
- 接口参数校验

数据库操作本身应该放到 Repository 层，连接层只提供统一入口。

## 4. 推荐文件位置

建议把 MongoDB 连接模块放在：

```bash
backend/
└── app/
    └── core/
        └── database.py
```

这样后续 `main.py`、`repositories/`、`services/` 都可以直接引用它。

## 5. 这一章需要准备什么

在开始写连接层之前，你需要已经具备以下内容：

- 配置类已经完成
- `mongo_uri` 和 `mongo_db_name` 已经统一进入配置对象
- Docker 里的 MongoDB 服务已经准备好
- 后续 Repository 层的目录已经规划好

如果这些还没准备好，建议先回到上一章补齐。

## 6. MongoDB 连接方式的选择

你的项目是 FastAPI 后端，建议使用异步 MongoDB 驱动，这样和 FastAPI 的异步风格更匹配。

推荐方案：

- MongoDB 驱动：`motor`
- 客户端对象：`AsyncIOMotorClient`
- 数据库对象：`AsyncIOMotorDatabase`

选择异步驱动的原因：

- 更适合 FastAPI
- 后续接口不会被同步 IO 阻塞
- 便于和异步 Agent 调用一起协作

## 7. 连接层应该有哪些能力

建议你的 `database.py` 至少提供以下能力：

1. 获取 MongoDB 客户端
2. 获取数据库对象
3. 初始化连接和索引
4. 关闭连接

这四个能力基本就足够支撑 demo 阶段。

## 8. 推荐实现结构

下面是推荐的模块设计思路，你可以照着实现：

```bash
database.py
├── settings 引用
├── 全局 client 变量
├── get_client()
├── get_database()
├── init_db()
└── close_db()
```

### 8.1 设计原则

- `get_client()` 只负责拿客户端
- `get_database()` 只负责拿数据库对象
- `init_db()` 只负责初始化索引和必要资源
- `close_db()` 只负责优雅关闭

这样职责会非常清晰。

## 9. 推荐实现代码

下面这份代码可以直接作为 `backend/app/core/database.py` 的参考实现。

```python
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings


settings = get_settings()

client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global client
    if client is None:
        client = AsyncIOMotorClient(settings.mongo_uri)
    return client


def get_database() -> AsyncIOMotorDatabase:
    return get_client()[settings.mongo_db_name]


async def init_db() -> None:
    database = get_database()
    await database.games.create_index("game_id", unique=True)
    await database.games.create_index("status")


async def close_db() -> None:
    global client
    if client is not None:
        client.close()
        client = None
```

## 10. 代码说明

### 10.1 为什么要有全局 client

MongoDB 客户端一般是长连接对象，不建议频繁创建和销毁。

因此这里使用一个全局变量保存客户端：

- 第一次调用时创建
- 后续调用直接复用

这可以减少重复连接带来的开销。

### 10.2 为什么要通过 get_database() 获取数据库

这样后续 Repository 层不需要自己拼 `mongo_uri`，也不需要关心数据库名，只要直接拿数据库对象即可。

### 10.3 为什么要创建索引

demo 阶段虽然数据量很小，但索引仍然值得提前做。

建议至少创建：

- `game_id` 唯一索引
- `status` 普通索引

原因：

- `game_id` 是游戏记录的唯一标识，不能重复
- `status` 后面常用于查询“进行中 / 已结束”的游戏

## 11. 应用生命周期接入方式

MongoDB 连接不应该只是“写个函数放在那里”，而应该接入 FastAPI 的应用生命周期。

建议在 `main.py` 里使用应用启动和关闭阶段去调用：

- 启动时：初始化连接和索引
- 关闭时：释放客户端

这样可以避免以下问题：

- 服务启动后数据库还没准备好
- 服务退出时连接没关闭
- 热重载或异常退出导致资源残留

## 12. 推荐接入方式

如果你使用 FastAPI 的 lifespan 方式，推荐按下面的思路接入：

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()
```

接着在创建 `FastAPI` 实例时，把这个 `lifespan` 传进去即可。

## 13. 连接参数应该从哪里来

你的连接参数已经在配置类中统一管理，所以数据库模块只应该从配置对象读取：

- `mongo_uri`
- `mongo_db_name`

不要在数据库模块中重新写一遍连接串，也不要把环境变量解析逻辑散落到别的地方。

## 14. 建议的环境变量

数据库连接目前建议至少支持这些环境变量：

- `MONGO_URI`
- `MONGO_DB_NAME`

如果以后要扩展副本集、认证数据库、超时参数，也可以继续补充，但 demo 阶段先保持最小集合。

## 15. Repository 层如何使用数据库连接

Repository 层不应该自己创建 MongoDB 客户端，而应该直接使用 `get_database()` 拿到数据库对象。

推荐使用方式是：

- Repository 初始化时获取数据库
- 通过集合对象执行查询和更新
- 让数据库连接保持统一入口

这样做可以避免在每个 Repository 文件里重复写连接逻辑。

## 16. 索引设计建议

这一步虽然还不是业务逻辑，但它对后续查询很重要。

建议至少考虑这些索引：

- `games.game_id`：唯一索引
- `games.status`：普通索引

如果后面你需要按创建时间或用户维度查询，也可以再加：

- `games.created_at`
- `games.user_id`

但 demo 阶段先不要一次性加太多。

## 17. 常见错误与避免方式

### 17.1 在每次请求里创建客户端

这是最常见的错误之一。MongoDB 客户端应该复用，而不是每次请求重新创建。

### 17.2 把数据库逻辑写进服务层

Service 层可以调用 Repository，但不要直接拼接 MongoDB 操作。

### 17.3 忘记创建索引

虽然 demo 也能跑，但建议一开始就把 `game_id` 唯一索引加上，避免后续数据重复。

### 17.4 忽略关闭连接

服务退出时最好关闭客户端，尤其是开发模式频繁重载时。

## 18. 这一章完成后的验收标准

你可以用下面几点判断 MongoDB 连接层是否完成：

- `database.py` 可以从配置中读取数据库地址和数据库名
- 应用启动时可以成功初始化 MongoDB 连接
- `games` 集合能够创建基础索引
- 应用关闭时可以释放客户端
- Repository 层可以直接拿到数据库对象

## 19. 这一章完成后再做什么

完成 MongoDB 连接层后，下一步建议去写 Repository 层手册。

因为此时你已经有了稳定的数据库入口，后面只需要围绕“如何读写数据”来设计具体仓库类即可，不需要再纠结连接问题。

## 20. 本章开发检查清单

- [ ] 已确认配置类中有 `mongo_uri` 和 `mongo_db_name`
- [ ] 已决定使用异步 MongoDB 驱动
- [ ] 已完成 `database.py` 文件设计
- [ ] 已支持客户端复用
- [ ] 已支持数据库对象获取
- [ ] 已支持启动初始化
- [ ] 已支持关闭释放
- [ ] 已创建必要索引
- [ ] 已避免在业务层重复创建连接

## 21. 最终建议

如果你只想先把 demo 跑起来，这一章的关键不是“把所有 MongoDB 功能都写完”，而是“让数据库连接成为一个稳定、统一、可复用的基础模块”。

只要这一层稳定，后面的游戏记录、回合记录、历史查询和复盘数据都能顺着这条链路往下做。
