# 用户游戏记录接口

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.games import get_game_service
from app.schemas.game_details import UserGameHistoryResponse
from app.services.game_service import GameService

router = APIRouter(prefix="/user/games", tags=["user-games"])


@router.get("/history", response_model=UserGameHistoryResponse)
async def get_user_game_history(
    user_id: str = Query(..., alias="userId"),
    service: GameService = Depends(get_game_service),
):
    try:
        return await service.get_user_game_history(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get user game history")