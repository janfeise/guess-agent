# 轮次锁测试

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

# 假设测试运行在 backend 目录


@pytest.mark.asyncio
async def test_turn_lock_phase_validation():
    """测试轮次锁的阶段和意图校验"""
    from app.services.game_service import GameService
    
    # 创建 mock 对象
    mock_settings = MagicMock()
    mock_agent = AsyncMock()
    mock_repository = AsyncMock()
    mock_memory_policy = MagicMock()
    
    service = GameService(
        settings=mock_settings,
        agent=mock_agent,
        repository=mock_repository,
        memory_policy=mock_memory_policy,
    )
    
    # 测试场景 1：user_turn 阶段只允许 question 和 guess
    game = {
        "game_id": "test_1",
        "status": "active",
        "history": [],
        "metadata": {
            "phase": "user_turn",
            "next_actor": "user",
            "expected_turn_type": "question",
        }
    }
    
    # 模拟 parse_user_intent 返回 answer
    mock_agent.parse_user_intent.return_value = {
        "intent": "answer",
        "answer": "yes",
        "confidence": 0.9,
    }
    
    mock_repository.get_game.return_value = game
    
    # 提交 answer 时应该被拒绝
    result = await service.submit_turn("test_1", "是", "agent", "input")
    assert result.get("message") == "现在轮到你提问或猜词，不是回答阶段"
    

@pytest.mark.asyncio
async def test_turn_lock_awaiting_answer_phase():
    """测试 awaiting_answer 阶段的轮次锁"""
    from app.services.game_service import GameService
    
    mock_settings = MagicMock()
    mock_agent = AsyncMock()
    mock_repository = AsyncMock()
    mock_memory_policy = MagicMock()
    
    service = GameService(
        settings=mock_settings,
        agent=mock_agent,
        repository=mock_repository,
        memory_policy=mock_memory_policy,
    )
    
    # 测试场景：awaiting_answer 阶段只允许 answer
    game = {
        "game_id": "test_2",
        "status": "active",
        "history": [],
        "metadata": {
            "phase": "awaiting_answer",
            "next_actor": "user",
            "expected_turn_type": "answer",
        }
    }
    
    # 模拟 parse_user_intent 返回 question
    mock_agent.parse_user_intent.return_value = {
        "intent": "question",
        "confidence": 0.9,
    }
    
    mock_repository.get_game.return_value = game
    
    # 提交 question 时应该被拒绝
    result = await service.submit_turn("test_2", "这是一道数学题吗？", "agent", "input")
    assert result.get("message") == "请先回答上一轮问题"


@pytest.mark.asyncio
async def test_turn_lock_returns_to_user_turn():
    """测试用户回答后返回 user_turn 阶段"""
    from app.services.game_service import GameService
    
    mock_settings = MagicMock()
    mock_settings.revelation_mode = "none"
    
    mock_agent = AsyncMock()
    mock_repository = AsyncMock()
    mock_memory_policy = MagicMock()
    mock_memory_policy.build_summary.return_value = "test_summary"
    
    service = GameService(
        settings=mock_settings,
        agent=mock_agent,
        repository=mock_repository,
        memory_policy=mock_memory_policy,
    )
    
    # 测试场景：用户回答后应该返回 user_turn
    game = {
        "game_id": "test_3",
        "status": "active",
        "history": [],
        "round_count": 1,
        "metadata": {
            "phase": "awaiting_answer",
            "next_actor": "user",
            "expected_turn_type": "answer",
        }
    }
    
    # 模拟 parse_user_intent 返回 answer
    mock_agent.parse_user_intent.return_value = {
        "intent": "answer",
        "answer": "yes",
        "confidence": 0.9,
        "reason": "user_answered_affirmatively",
    }
    
    mock_repository.get_game.return_value = game
    
    # 提交 answer
    result = await service.submit_turn("test_3", "是", "agent", "input")
    
    # 检查 update_game_state 是否被调用了正确的参数
    mock_repository.update_game_state.assert_called_once()
    call_kwargs = mock_repository.update_game_state.call_args[1]
    
    # 验证阶段和轮次锁字段
    assert call_kwargs.get("phase") == "user_turn"
    assert call_kwargs.get("next_actor") == "user"
    assert call_kwargs.get("expected_turn_type") == "question"
    assert result.get("phase") == "user_turn"
    assert result.get("message") == "回答已记录，现在轮到你提问或猜词。"


@pytest.mark.asyncio
async def test_turn_lock_state_consistency():
    """测试轮次锁状态的一致性"""
    from app.services.game_service import GameService
    
    mock_settings = MagicMock()
    mock_agent = AsyncMock()
    mock_repository = AsyncMock()
    mock_memory_policy = MagicMock()
    
    service = GameService(
        settings=mock_settings,
        agent=mock_agent,
        repository=mock_repository,
        memory_policy=mock_memory_policy,
    )
    
    # 验证 _get_turn_lock_state 返回正确的值
    game = {
        "game_id": "test_4",
        "metadata": {
            "phase": "awaiting_judgement",
            "next_actor": "user",
            "expected_turn_type": "judge",
            "last_actor": "system",
            "last_intent": "guess",
        }
    }
    
    turn_lock_state = service._get_turn_lock_state(game)
    
    assert turn_lock_state["phase"] == "awaiting_judgement"
    assert turn_lock_state["next_actor"] == "user"
    assert turn_lock_state["expected_turn_type"] == "judge"


@pytest.mark.asyncio  
async def test_turn_lock_intent_validation():
    """测试轮次锁的意图校验"""
    from app.services.game_service import GameService
    
    mock_settings = MagicMock()
    mock_agent = AsyncMock()
    mock_repository = AsyncMock()
    mock_memory_policy = MagicMock()
    
    service = GameService(
        settings=mock_settings,
        agent=mock_agent,
        repository=mock_repository,
        memory_policy=mock_memory_policy,
    )
    
    # 测试 _is_turn_allowed 函数
    
    # user_turn 允许 question 和 guess
    assert service._is_turn_allowed("user_turn", "question") == True
    assert service._is_turn_allowed("user_turn", "guess") == True
    assert service._is_turn_allowed("user_turn", "answer") == False
    assert service._is_turn_allowed("user_turn", "judge") == False
    
    # awaiting_answer 只允许 answer
    assert service._is_turn_allowed("awaiting_answer", "answer") == True
    assert service._is_turn_allowed("awaiting_answer", "question") == False
    assert service._is_turn_allowed("awaiting_answer", "judge") == False
    
    # awaiting_judgement 允许 judge 和 answer
    assert service._is_turn_allowed("awaiting_judgement", "judge") == True
    assert service._is_turn_allowed("awaiting_judgement", "answer") == True
    assert service._is_turn_allowed("awaiting_judgement", "question") == False


def test_build_initial_metadata():
    """测试初始元数据中的轮次锁字段"""
    from app.services.game_service import GameService
    
    metadata = GameService._build_initial_metadata()
    
    # 验证所有轮次锁字段都存在
    assert metadata.get("phase") == "user_turn"
    assert metadata.get("next_actor") == "user"
    assert metadata.get("expected_turn_type") == "question"
    assert metadata.get("last_actor") == "system"
    assert metadata.get("last_intent") is None
    assert metadata.get("awaiting_judgement") == False
    assert metadata.get("awaiting_answer") == False
    assert metadata.get("game_mode") == "dual_word_isolated"
    assert metadata.get("reasoning_scope") == "user_word"
