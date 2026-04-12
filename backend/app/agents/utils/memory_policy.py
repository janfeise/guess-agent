# 记忆策略
""" 
- 按 game_id 管理上下文
- 只保留当前局有用的内容
- 对过长上下文进行截断
- 对更早内容进行摘要压缩
 """

class MemoryPolicy:
    def __init__(self, max_rounds: int = 8):
        self.max_rounds = max_rounds # 每局最多保留的轮数

    def build_recent_history(self, game_history: list[dict]) -> list[dict]:
        # 从游戏历史中提取最近的 max_rounds 轮对话
        if len(game_history) <= self.max_rounds:
            return game_history
        
        return game_history[-self.max_rounds:] # 获取最近的 max_rounds 轮对话
    
    def build_summary(self, game_history: list[dict]) -> str:
        # 对游戏历史进行摘要压缩，保留关键信息
        # 这里可以使用简单的规则或者调用外部模型进行摘要
        old_history = game_history[:-self.max_rounds] # 获取较早的对话历史
        if not old_history:
            return ""
        
        summary_parts: list[str] = []
        for item in old_history:
            question = item.get("question", "")
            answer = item.get("answer", "")
            summary_parts.append(f"Q:{question} A:{answer}")

        return "；".join(summary_parts)