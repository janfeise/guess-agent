# Guess Agent

一个基于AI代理的智能猜词游戏平台，融合LLM能力进行实时交互和答案验证。

## 项目结构

```
guess-agent/
├── backend/              # Python 后端服务
│   ├── app/
│   │   ├── main.py       # 应用入口
│   │   ├── agents/       # AI Agent 实现
│   │   ├── api/          # API 路由
│   │   ├── services/     # 业务逻辑
│   │   └── utils/        # 工具函数
│   ├── requirements.txt   # 依赖包
│   └── tests/            # 单元测试
├── fronted/              # 前端应用
│   ├── guess-agent-fronted/      # React + TypeScript
│   ├── guess-agent-fronted2/     # Vue + UniApp
│   └── stitch_app/               # 原型设计
├── docker/               # Docker 配置
│   ├── backend.Dockerfile
│   └── docker-compose.yml
└── 文档/                 # 项目文档和实施指南
```

## 快速开始

### 后端部署

1. 创建虚拟环境
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS
```

2. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库、API key 等
```

4. 运行服务
```bash
python app/main.py
```

### Docker 部署

```bash
docker-compose -f docker/docker-compose.yml up -d
```

### 前端开发

**React 版本：**
```bash
cd fronted/guess-agent-fronted
npm install
npm run dev
```

**Vue 版本：**
```bash
cd fronted/guess-agent-fronted2
npm install
npm run dev
```

## 核心功能

- 智能猜词游戏引擎
- AI Agent 辅助推理
- 实时多轮对话
- 游戏历史记录
- 用户积分系统

## 主要技术栈

**后端：**
- Python 3.8+
- FastAPI / Flask
- MongoDB
- LLM API (OpenAI / 其他)

**前端：**
- React 18 + TypeScript
- Vue 3
- UniApp (跨端)
- Vite

**基础设施：**
- Docker
- Docker Compose

## 环境配置

项目需要以下环境变量（在 `.env` 文件中配置）：

```
# MongoDB
MONGODB_URL=mongodb://localhost:27017

# LLM API
OPENAI_API_KEY=your_api_key
LLM_MODEL=gpt-4

# 应用配置
DEBUG=false
SECRET_KEY=your_secret_key
```

**注意：** `.env` 文件包含敏感信息，不会被上传到版本控制系统。

## 文档

项目包含详细的实施指南和技术文档，位于 `文档/` 目录：

- `猜词 Agent 项目文档.md` - 项目总体设计
- `后端代码指导说明手册.md` - 后端实现指南
- `Agent代码实现文档.md` - Agent 逻辑文档
- `backend编码顺序/` - 分阶段实施清单

## 开发工作流

1. 创建特性分支
2. 进行开发和测试
3. 提交 Pull Request
4. Code Review
5. 合并到 main 分支

## 许可证

MIT

## 联系方式

如有问题或建议，请提交 Issue 或 PR。
