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

    async def list_games_by_owner(self, owner_id: str):
        cursor = self.collection.find({"owner_id": owner_id}).sort("updated_at", -1)
        return await cursor.to_list(length=None)
    
    async def update_game_state(
            self,
            game_id: str,
            history: list[dict] | None = None,
            summary: str | None = None,
            round_count: int | None = None,
            phase: str | None = None,
            awaiting_judgement: bool = False,
            waiting_answer: bool = False,
            pending_guess: str = "",
            pending_question: str = "",
            agent_confidence: float = 0.0,
            last_actor: str | None = None,
            last_intent: str | None = None,
            game_mode: str | None = None,
            reasoning_scope: str | None = None,
            next_actor: str | None = None,
            expected_turn_type: str | None = None,
    ):
        update_fields = {
            "history": history,
            "summary": summary,
            "round_count": round_count,
            "metadata.phase": phase,
            "metadata.awaiting_judgement": awaiting_judgement,
            "metadata.waiting_answer": waiting_answer,
            "metadata.pending_guess": pending_guess,
            "metadata.pending_question": pending_question,
            "metadata.agent_confidence": agent_confidence,
            "updated_at": datetime.utcnow(),
        }

        if last_actor is not None:
            update_fields["metadata.last_actor"] = last_actor
        if last_intent is not None:
            update_fields["metadata.last_intent"] = last_intent
        if game_mode is not None:
            update_fields["metadata.game_mode"] = game_mode
        if reasoning_scope is not None:
            update_fields["metadata.reasoning_scope"] = reasoning_scope
        if next_actor is not None:
            update_fields["metadata.next_actor"] = next_actor
        if expected_turn_type is not None:
            update_fields["metadata.expected_turn_type"] = expected_turn_type

        result = await self.collection.update_one(
            {"game_id": game_id},
            {
                "$set": update_fields
            }
        )

        if result.matched_count == 0:
            raise ValueError(f"Game with id {game_id} not found")
        
        return result
