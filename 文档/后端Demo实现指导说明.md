# 后端 Demo 实现指导说明

## 1. 目标

这份说明文档用于指导你先做出一个能跑通的后端 demo。目标不是一次性做完整产品，而是先把最小闭环搭起来：

- Docker 能一键启动后端与 MongoDB
- FastAPI 服务能正常响应
- LangChain 能接入 DeepSeek 并完成一次最小问答
- MongoDB 能保存最基础的游戏状态
- 能用接口直接验证 demo 是否可用

本阶段只做后端，不包含前端联调、不做生产级部署，也不追求复杂 Agent 能力。

## 2. Demo 范围

### 必做内容

- 后端服务基础骨架
- Docker Compose 启动环境
- DeepSeek 接入
- LangChain 最小调用链路
- MongoDB 连接与基础持久化
- 一个可测试的对话接口

### 暂不做内容

- 前端页面
- WebSocket 多人对战
- 向量数据库
- 复杂记忆系统
- 多 Agent 协作
- 完整权限体系

## 3. 建议目录

建议沿用现有目录思路，只先落地 demo 需要的最小文件：

```bash
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── api/
│   │   └── v1/
│   │       ├── game.py
│   │       └── agent.py
│   ├── services/
│   │   ├── game_service.py
│   │   └── agent_service.py
│   ├── agents/
│   │   ├── guess_agent.py
│   │   └── prompt/
│   │       └── system.txt
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   └── utils/
├── requirements.txt
└── run.py

docker/
├── docker-compose.yml
├── backend.Dockerfile
└── mongo-init.js
```

## 4. 技术选型

demo 阶段保持和当前文档一致：

- 后端：FastAPI
- Agent：LangChain Python
- 模型：DeepSeek-V3.2
- 数据库：MongoDB
- 部署：Docker + Docker Compose

如果后续要扩展，只需要在这个最小版本上叠加服务层、工具层和更复杂的记忆机制。

## 5. 最小实现思路

### 5.1 启动入口

先让 FastAPI 跑起来，提供两个基础能力：

- 健康检查接口
- 对话接口

健康检查用于确认服务在线，对话接口用于验证 LangChain 和 DeepSeek 是否连通。

### 5.2 LangChain 最小接入

demo 阶段只保留最小链路：

1. 接收用户问题
2. 读取基础 system prompt
3. 调用 DeepSeek
4. 返回回答

这一步不做复杂工具调用，不做多轮记忆增强，只保留必要上下文即可。

### 5.3 MongoDB 最小持久化

只存最基础的数据即可：

- game_id
- user_answer_encrypted
- agent_answer_encrypted
- rounds
- status

如果 demo 只是验证链路，也可以先存少量字段，后面再补。

## 6. Docker 启动方案

### 6.1 服务拆分

建议至少包含两个服务：

- backend：FastAPI 服务
- mongo：MongoDB 服务

### 6.2 环境变量

建议准备一个 .env 文件，至少包含：

- AGENT_MODEL_API_KEY
- AGENT_MODEL_BASE_URL
- AGENT_MODEL_NAME
- AGENT_MODEL_TEMPERATURE
- HELPER_MODEL_API_KEY
- HELPER_MODEL_BASE_URL
- HELPER_MODEL_NAME
- HELPER_MODEL_TEMPERATURE
- MONGO_URI
- MONGO_DB_NAME
- APP_HOST
- APP_PORT

### 6.3 启动方式

推荐使用 Docker Compose 一次性启动。

示例运行顺序：

1. 配置环境变量
2. 构建后端镜像
3. 启动 MongoDB
4. 启动 FastAPI
5. 访问健康检查接口
6. 访问对话接口验证链路

## 7. LangChain 最小实现

### 7.1 Agent 责任边界

demo 阶段的 Agent 不需要承担完整游戏逻辑，只负责：

- 接收问题
- 结合提示词生成回答
- 保持基础上下文

如果后续要接入小助手，也建议让小助手独立使用自己的模型配置和提示词，不和主模型共用同一套参数。

### 7.2 Prompt 要求

system prompt 需要明确：

- 这是一个猜词游戏助手
- 不允许直接泄露答案
- 回答要简洁
- 只能基于当前上下文推理

### 7.3 推荐实现顺序

1. 先实现直接调用 DeepSeek 的最小链路
2. 再包一层 LangChain
3. 最后补 MongoDB 记录

这样可以先确认模型可用，再补框架层。

## 8. MongoDB 最小数据结构

建议先使用一个 game 集合。

示例字段：

- \_id
- game_id
- status
- created_at
- updated_at
- user_answer_encrypted
- agent_answer_encrypted
- rounds

rounds 可以是数组，每一项记录：

- question
- answer
- note
- created_at

## 9. 接口建议

demo 至少准备两个接口：

### 9.1 健康检查

用于确认服务是否启动成功。

### 9.2 对话接口

用于发送用户问题并获取 Agent 返回。

建议对话接口先做成单轮请求，后面再加 game_id 关联历史记录。

## 10. 实施顺序

建议按下面顺序做，能最快跑通：

1. 搭 FastAPI 基础骨架
2. 加健康检查接口
3. 接入 DeepSeek 基础调用
4. 用 LangChain 包装问答链路
5. 接 MongoDB
6. 保存一条 game 记录
7. 用 Docker Compose 启动整套环境
8. 用接口工具验证流程

## 11. 验收 Checklist

- [ ] Docker Compose 可以成功启动 MongoDB
- [ ] FastAPI 服务可以正常启动
- [ ] 健康检查接口返回成功
- [ ] DeepSeek API Key 配置正确
- [ ] LangChain 可以收到问题并返回结果
- [ ] MongoDB 可以写入一条 game 数据
- [ ] 对话接口可以完成一次完整请求
- [ ] 容器重启后服务仍可恢复

## 12. 常见问题

### 12.1 DeepSeek 调用失败

先检查 API Key、Base URL、模型名是否正确，再检查网络是否能访问外部服务。

### 12.2 MongoDB 连接失败

先确认容器是否启动成功，再检查 MONGO_URI 是否写对，最后检查端口是否被占用。

### 12.3 接口返回异常

优先查看后端日志，确认是参数缺失、模型报错，还是数据库异常。

### 12.4 容器启动太慢

第一次构建镜像会慢，属于正常现象。后续可以通过缓存依赖层来优化。

## 13. 建议的下一步

当这个 demo 跑通后，再补下面几项：

- game_service 的完整流程控制
- 更明确的回合记录
- 加密模块接入
- 小助手接口
- 前端联调

这份 demo 的核心不是复杂，而是先把链路跑通，确保后续扩展不会推翻重来。
