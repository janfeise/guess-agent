# 游戏问答接口

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

# 导入项目内部模块
from app.agents.utils.memory_policy import MemoryPolicy
from app.core.config import get_settings
from app.core.database import get_database
from app.repositories.game_repository import GameRepository
from app.services.game_service import GameService

class SubmitTurnRequest(BaseModel):
    question: str = Field(..., description="玩家提交的问题")
    mode: str = Field(default="agent", description="回答模式，默认为 'agent'，可选 'helper'")

router = APIRouter(prefix="/games", tags=["games"])

def get_game_service() -> GameService:
    settings = get_settings()
    repository = GameRepository(get_database())
    memory_policy = MemoryPolicy(max_rounds=8)
    return GameService(settings, agent=None, repository=repository, memory_policy=memory_policy)

@router.post("/{game_id}/turns")
async def submit_turn(game_id: str, request: SubmitTurnRequest, service: GameService = Depends(get_game_service)):
    try:
        return await service.submit_turn(game_id, request.question, request.mode)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to submit turn")