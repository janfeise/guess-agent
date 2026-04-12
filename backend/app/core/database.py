# mongodb 数据库连接和操作封装

# 导入配置函数，获取数据库连接字符串和数据库名称等配置项
from app.core.config import get_settings

# 异步连接MongoDB的库，提供了异步操作接口
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

settings = get_settings()

# 全局 MongoDB 客户端实例，应用启动时创建，应用关闭时关闭连接
client: AsyncIOMotorClient | None = None

# 初始化
def get_client() -> AsyncIOMotorClient:
    global client
    if client is None:
        client = AsyncIOMotorClient(settings.mongo_uri)
    return client

# 获取数据库实例
def get_database() -> AsyncIOMotorDatabase:
    return get_client()[settings.mongo_db_name]

# 初始化数据库连接，应用启动时调用
async def init_db() -> None:
    database = get_database()
    await database.games.create_index("game_id", unique=True)  # 创建游戏索引
    await database.games.create_index("status")  # 创建状态索引

# 关闭数据库连接，应用关闭时调用
async def close_db() -> None:
    global client
    if client is not None:
        client.close()
        client = None