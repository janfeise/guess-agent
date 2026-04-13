# 游戏问答接口

import logging
from pathlib import Path
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

# 导入项目内部模块
from app.agents.guess_agent_fixed import GuessAgent
from app.agents.utils.memory_policy import MemoryPolicy
from app.agents.utils.prompt_loader import PromptLoader
from app.core.config import get_settings
from app.core.database import get_database
from app.repositories.game_repository import GameRepository
from app.services.game_service import GameService

logger = logging.getLogger(__name__)

class SubmitTurnRequest(BaseModel):
    turn_type: Literal["input", "answer", "judge"] = Field(default="input", description="回合类型，input表示普通输入，answer表示玩家回答系统问题，judge表示玩家确认系统猜词结果")
    question: str | None = Field(default=None, description="兼容旧客户端的输入字段")
    content: str | None = Field(default=None, description="玩家输入内容")
    judgement: bool | None = Field(default=None, description="玩家确认系统是否猜词正确")
    mode: str = Field(default="agent", description="回答模式，默认为 'agent'，可选 'helper'")

class SubmitTurnResponse(BaseModel):
    game_id: str = Field(..., description="游戏ID")
    status: str = Field(..., description="当前状态")
    phase: str = Field(..., description="当前阶段")
    result: str = Field(..., description="当前结果")
    answer: str | None = Field(default=None, description="内部判断结果，yes/no/unknown")
    response_text: str | None = Field(default=None, description="给用户看的自然语言回复")
    answer_text: str | None = Field(default=None, description="兼容旧客户端的用户回复文本")
    hint: str | None = Field(default=None, description="简短提示信息")
    confidence: float | None = Field(default=None, description="判断把握度")
    history: list[dict] = Field(..., description="游戏历史记录")

router = APIRouter(prefix="/games", tags=["games"])

def get_game_service() -> GameService:
    settings = get_settings()
    repository = GameRepository(get_database())
    prompt_loader = PromptLoader(str(Path(__file__).resolve().parents[2] / "agents" / "prompt"))
    memory_policy = MemoryPolicy(max_rounds=8)
    agent = GuessAgent(settings, prompt_loader, memory_policy)
    return GameService(settings, agent=agent, repository=repository, memory_policy=memory_policy)

@router.post("/{game_id}/turns")
async def submit_turn(game_id: str, request: SubmitTurnRequest, service: GameService = Depends(get_game_service)):
    user_text = request.content or request.question or ""
    if request.turn_type == "judge":
        user_text = "是" if request.judgement else "否"

    logger.info(
        "收到回合请求: game_id=%s turn_type=%s mode=%s text=%s",
        game_id,
        request.turn_type,
        request.mode,
        (user_text[:120] if user_text else ""),
    )

    try:
        result = await service.submit_turn(game_id, user_text, request.mode, request.turn_type)
        # 清理 history 中的敏感信息（避免泄露答案）
        if "history" in result and result["history"]:
            result["history"] = service.sanitize_history_for_client(result["history"])
        return result
    except ValueError as exc:
        logger.warning("回合请求参数或业务错误: game_id=%s error=%s", game_id, exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.exception("回合请求处理失败: game_id=%s error=%s", game_id, exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to submit turn")