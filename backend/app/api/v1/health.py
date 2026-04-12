# 健康检查：这是一个简单的健康检查接口，返回服务的状态信息

# 配置函数导入
from app.core.config import get_settings
from app.core.database import get_database

# 导入 fastapi
from fastapi import APIRouter, HTTPException

# 导入 datetime 模块，用于返回当前时间戳
from datetime import datetime, timezone

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    settings = get_settings()
    database_status = "ready"
    database = get_database()

    try:
        await database.command("ping")
    except Exception:
        database_status = "not_ready"

    return {
        "status": "ok",
        "service": settings.app_name,
        "database": database_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }