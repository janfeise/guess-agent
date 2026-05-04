# 后端入口文件

# 导入配置函数
import logging

from app.api.v1.health import router as health_router
from app.api.game_details import router as game_details_router
from app.api.user_games import router as user_games_router
from app.api.v1.games import router as games_router
from app.api.v1.submit_turn import router as submit_turn_router
from app.core.config import get_settings
from app.core.database import init_db, close_db

# 导入 FastAPI 框架
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 导入异步上下文管理器
from contextlib import asynccontextmanager

settings = get_settings()

def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
        force=True,
    )
    logging.getLogger().setLevel(logging.INFO)
    for logger_name in ["app", "app.api", "app.agents", "app.core", "app.repositories", "app.services", "uvicorn", "uvicorn.error", "uvicorn.access"]:
        logging.getLogger(logger_name).setLevel(logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    _configure_logging()
    # 应用启动时初始化数据库连接
    await init_db()

    # 应用运行期间保持数据库连接，处理请求
    yield

    # 应用关闭时关闭数据库连接
    await close_db()

# 创建 FastAPI 应用实例，指定生命周期函数
app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

# 允许的前端源
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # 允许的来源
    allow_credentials=True,
    allow_methods=["*"],          # 允许所有方法
    allow_headers=["*"],          # 允许所有头
)

# 注册路由
app.include_router(health_router, prefix="/api/v1")
app.include_router(game_details_router, prefix="/api")
app.include_router(user_games_router, prefix="/api")
app.include_router(games_router, prefix="/api/v1")
app.include_router(submit_turn_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": settings.app_name,
    }