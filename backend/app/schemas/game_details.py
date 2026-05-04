from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class GameDetailsResponse(BaseModel):
    game_id: str = Field(..., description="游戏ID")
    status: str = Field(..., description="游戏状态")
    owner_id: str | None = Field(default=None, description="游戏创建者的用户ID")
    difficulty: str | None = Field(default=None, description="游戏难度")
    user_word: str | None = Field(default=None, description="玩家输入的开局词")
    round_count: int = Field(default=0, description="当前轮次")
    summary: str = Field(default="", description="游戏摘要")
    history: list[dict[str, Any]] = Field(default_factory=list, description="历史回合记录")
    metadata: dict[str, Any] = Field(default_factory=dict, description="游戏状态元数据")
    progress: dict[str, Any] | None = Field(default=None, description="进行中游戏的当前进度")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    finished_at: datetime | None = Field(default=None, description="结束时间")
    finish_reason: str | None = Field(default=None, description="结束原因")
    system_word_encrypted: str | None = Field(default=None, description="系统词密文")
    target_word_source: str | None = Field(default=None, description="系统词来源")


class UserGameHistoryResponse(BaseModel):
    user_id: str = Field(..., description="用户ID")
    total: int = Field(..., description="游戏记录总数")
    games: list[GameDetailsResponse] = Field(default_factory=list, description="统一格式化后的游戏记录")
