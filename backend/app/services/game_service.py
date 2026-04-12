# 游戏service层，负责处理游戏相关的业务逻辑

# 导入 id 生成和时间处理库
import uuid
from datetime import datetime

# 导入 stream_chunk 用于流式传输
from app.agents.utils.streaming import (
    build_stream_chunk,
    build_stream_end,
)

# 导入加密函数，获取随机字符
import secrets

from app.core.security import encrypt
from app.core.constants import validate_start_word

class GameService:
    def __init__(self, settings, agent, repository, memory_policy):
        self.settings = settings
        self.agent = agent
        self.repository = repository
        self.memory_policy = memory_policy

    async def create_game(self, owner_id=None, user_word: str | None = None, difficulty: str | None = None):
        if not user_word:
            raise ValueError("开局词不能为空")
        normalized_user_word = validate_start_word(user_word)

        # 创建一个新的游戏实例
        game_id = str(uuid.uuid4()) # 生成唯一的game_id，可以使用UUID或者其他方法
        now = datetime.now() # 获取当前时间戳

        # 调用小助手api获取一个随机的词
        target_word = await self.agent.generate_start_word(difficulty=difficulty)
        normalized_system_word = validate_start_word(target_word)
        system_password = secrets.token_hex(16) # 生成一个随机的系统密码，用于加密存储目标词

        system_password_encrypted = encrypt(system_password, self.settings.encryption_secret)
        system_word_encrypted = encrypt(normalized_system_word, system_password_encrypted)

        game_doc = {
            "game_id": game_id,
            "owner_id": owner_id,
            "status": "active",
            "history": [],
            "summary": "",
            "round_count": 0,
            "created_at": now,
            "updated_at": now,
            "metadata": {},
            "difficulty": difficulty or "medium",
            "user_word": normalized_user_word,
            "system_word": normalized_system_word, 
            "system_word_encrypted": system_word_encrypted,
            "system_password_encrypted": system_password_encrypted,
            "target_word_source": "helper_llm"
        }

        await self.repository.create_game(game_doc)

        return {
            "game_id": game_id,
            "status": "active",
            "round_count": 0,
            "difficulty": difficulty or "medium",
            "user_word": normalized_user_word,
            "system_word_encrypted": system_word_encrypted,
            "created_at": now,
        }

    async def get_game(self, game_id: str):
        # 根据game_id获取游戏实例，查询游戏记录，判断游戏是否存在，返回完整文档或视图对象
        game = await self.repository.get_game(game_id)
        if not game:
            raise ValueError(f"Game with id {game_id} not found")
        return game

    async def submit_turn(self, game_id: str, question: str, mode: str = "agent"):
        # 提交一个新的回合，处理用户问题，调用agent生成回答，更新游戏记录，返回回答内容
        game = await self.repository.get_game(game_id)
        if not game:
            raise ValueError(f"Game with id {game_id} not found")
        
        if game.get("status") == "finished":
            raise ValueError(f"Game with id {game_id} has already finished")
        
        history = game.get("history", [])
        result = await self.agent.answer(question, history, mode)
        updated_history = result["history"]

        # 将新的对话轮次添加到游戏历史中，并更新游戏记录到数据库
        await self.repository.update_game_history(
            game_id, 
            history=updated_history,
            summary=self.memory_policy.build_summary(updated_history),
            round_count=len(updated_history),
        )

        return {
            "game_id": game_id,
            "question": question,
            "answer": result["answer"],
            "history": updated_history,
        }

    async def submit_turn_stream(self, game_id: str, question: str, mode: str = "agent"):
        # 提交一个新的回合，处理用户问题，调用agent生成回答，更新游戏记录，返回一个异步生成器用于流式传输回答内容
        game = await self.repository.get_game(game_id)
        if not game:
            raise ValueError(f"Game with id {game_id} not found")
        
        if game.get("status") == "finished":
            raise ValueError(f"Game with id {game_id} has already finished")
        
        history = game.get("history", [])
        full_answer_chunks: list[dict] = []

        yield build_stream_chunk()

        try:
            async for chunk in self.agent.stream_answer(question, history, mode):
                if chunk.get("type") == "chunk":
                    full_answer_chunks += chunk.get("content", "")
            yield chunk

            # 在流式传输完成后，更新游戏记录到数据库
            updated_history = history + [{"question": question, "answer": "".join(full_answer_chunks)}]
            await self.repository.update_game_history(
                game_id, 
                history=updated_history,
                summary=self.memory_policy.build_summary(updated_history),
                round_count=len(updated_history),
            )

            # 结束
            yield build_stream_end()

        except Exception as e:
            print(f"Error occurred while streaming answer: {e}")
            yield build_stream_chunk("Sorry, I encountered an error while processing your request.")
            raise e



    async def end_game(self, game_id: str, reason: str = "manual"):
        # 结束游戏，更新游戏状态和结束原因
        game = await self.repository.get_game(game_id)
        if not game:
            raise ValueError(f"Game with id {game_id} not found")   
        
        if game.get("status") == "finished":
            return game
        
        now = datetime.now()
        await self.repository.finish_game(
            game_id, 
            reason=reason, 
            finished_at=now
        )

        return {
            "game_id": game_id,
            "status": "finished",
            "finished_at": now,
            "reason": reason,
        }
