class TurnLock:
    """
    guess-agent 轮次锁管理器
    负责游戏状态机逻辑校验与状态更新
    """

    @staticmethod
    def get_state(game: dict) -> dict:
        """从游戏数据中提取当前的轮次锁状态"""
        metadata = game.get("metadata", {}) or {}
        return {
            "phase": metadata.get("phase", "user_turn"),
            "next_actor": metadata.get("next_actor", "user"),
            "expected_turn_type": metadata.get("expected_turn_type", "question"),
            "last_actor": metadata.get("last_actor", "system"),
            "last_intent": metadata.get("last_intent"),
        }

    @staticmethod
    def _get_turn_lock_state(game: dict) -> dict:
        metadata = game.get("metadata", {}) or {}
        return {
            "phase": metadata.get("phase", "user_turn"),
            "next_actor": metadata.get("next_actor", "user"),
            "expected_turn_type": metadata.get("expected_turn_type", "question"),
            "last_actor": metadata.get("last_actor", "system"),
            "last_intent": metadata.get("last_intent"),
        }

    @staticmethod
    def build_update(*, phase: str, next_actor: str, expected_turn_type: str, 
                     last_actor: str, last_intent: str) -> dict:
        """统一生成用于更新数据库的 metadata 字典"""
        return {
            "phase": phase,
            "next_actor": next_actor,
            "expected_turn_type": expected_turn_type,
            "last_actor": last_actor,
            "last_intent": last_intent,
        }