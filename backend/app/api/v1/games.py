# 游戏接口

# 导入标准库
from datetime import datetime
from pathlib import Path

# 导入 fastapi 和相关模块
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

# 导入项目内部模块
from app.agents.guess_agent import GuessAgent
from app.agents.utils.prompt_loader import PromptLoader
from app.agents.utils.memory_policy import MemoryPolicy
from app.core.config import get_settings
from app.core.database import get_database
from app.repositories.game_repository import GameRepository
from app.schemas.game_details import GameDetailsResponse
from app.services.game_service import GameService

class CreateGameRequest(BaseModel):
    owner_id: str | None = Field(default=None, description="游戏创建者的用户ID，可以为空")
    user_word: str = Field(..., description="玩家输入的开局词，长度不超过10个字符")
    difficulty: str | None = Field(default="medium", description="游戏难度，可以是easy、medium、hard之一")

class CreateGameResponse(BaseModel):
    game_id: str = Field(..., description="游戏ID")
    status: str = Field(..., description="游戏状态")
    round_count: int = Field(..., description="当前轮次")
    user_word: str = Field(..., description="玩家输入的开局词")
    difficulty: str = Field(..., description="游戏难度")
    system_word_encrypted: str = Field(..., description="系统词密文")
    created_at: datetime = Field(..., description="创建时间")

router = APIRouter(prefix="/games", tags=["games"])

def get_game_service() -> GameService:
    settings = get_settings()
    repository = GameRepository(get_database())
    prompt_loader = PromptLoader(str(Path(__file__).resolve().parents[2] / "agents" / "prompt"))
    memory_policy = MemoryPolicy(max_rounds=8)
    agent = GuessAgent(settings, prompt_loader, memory_policy)
    return GameService(settings, agent=agent, repository=repository, memory_policy=memory_policy)

@router.post("", response_model=CreateGameResponse, status_code=status.HTTP_201_CREATED)
async def create_game(request: CreateGameRequest, service: GameService = Depends(get_game_service)):
    try:
        return await service.create_game(owner_id=request.owner_id, user_word=request.user_word, difficulty=request.difficulty)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create game")


@router.get("/{game_id}", response_model=GameDetailsResponse)
async def get_game_details_compat(
    game_id: str,
    user_id: str | None = Query(default=None, alias="userId"),
    service: GameService = Depends(get_game_service),
):
    try:
        return await service.get_game_details(game_id, user_id=user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get game details")