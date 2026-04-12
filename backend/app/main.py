# 后端入口文件

# 导入配置函数
from app.api.v1.health import router as health_router
from app.api.v1.games import router as games_router
from app.core.config import get_settings
from app.core.database import init_db, close_db

# 导入 FastAPI 框架
from fastapi import FastAPI

# 导入异步上下文管理器
from contextlib import asynccontextmanager

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
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

# 注册路由
app.include_router(health_router, prefix="/api/v1")
app.include_router(games_router, prefix="/api/v1")
@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": settings.app_name,
    }