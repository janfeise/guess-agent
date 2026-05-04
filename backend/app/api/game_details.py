# 游戏详情接口

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.games import get_game_service
from app.schemas.game_details import GameDetailsResponse
from app.services.game_service import GameService

router = APIRouter(prefix="/game", tags=["game-details"])


@router.get("/{game_id}/details", response_model=GameDetailsResponse)
async def get_game_details(
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
