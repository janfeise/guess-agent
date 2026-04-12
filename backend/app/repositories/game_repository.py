# 游戏数据访问层，负责与 MongoDB 进行交互，提供游戏相关的数据操作接口

# 导入时间库
from datetime import datetime

class GameRepository:
    def __init__(self, db):
        self.db = db
        self.collection = self.db["games"]

    async def create_game(self, game_doc: dict):
        # 在数据库中创建一个新的游戏记录

        # 判断是否已经存在相同 game_id 的游戏记录，如果存在则抛出异常
        existing_game = await self.collection.find_one({"game_id": game_doc["game_id"]})
        if existing_game:
            raise ValueError(f"Game with id {game_doc['game_id']} already exists")

        await self.collection.insert_one(game_doc)
        return game_doc
    
    async def get_game(self, game_id: str):
        # 根据 game_id 从数据库中查询游戏记录，返回完整文档或视图对象
        game = await self.collection.find_one({"game_id": game_id})
        return game
    
    async def update_game_history(self, game_id: str, history: list[dict], summary: str, round_count: int):
        result = await self.collection.update_one(
            {"game_id": game_id},
            {
                "$set": {
                    "history": history,
                    "summary": summary,
                    "round_count": round_count,
                    "updated_at": datetime.utcnow(),
                }
            }
        )

        # 如果没有匹配到任何记录，说明 game_id 不存在，抛出异常
        if result.matched_count == 0:
            raise ValueError(f"Game with id {game_id} not found")
        
        return result
    
    async def finish_game(self, game_id: str, reason: str, finished_at):
        result = await self.collection.update_one(
            {"game_id": game_id},
            {
                "$set": {
                    "status": "finished",
                    "finished_at": finished_at,
                    "finish_reason": reason,
                    "updated_at": datetime.utcnow(),
                }
            }
        )

        # 如果没有匹配到任何记录，说明 game_id 不存在，抛出异常
        if result.matched_count == 0:
            raise ValueError(f"Game with id {game_id} not found")
        
        return result
    
    async def list_games(self, filter_query: dict | None = None, limit: int = 20, skip: int = 0):
        query = filter_query or {}

        cursor = self.collection.find(query).sort("updated_at", -1).skip(skip).limit(limit)
        
        return await cursor.to_list(length=limit)
