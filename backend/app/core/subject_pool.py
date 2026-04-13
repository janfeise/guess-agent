# 学科池，随机选择三个学科，动态拼接prompt给小助手

import random
from typing import List, Dict

DEFAULT_SUBJECT_COUNT = 3 # 每局游戏随机选择的学科数量

class SubjectPool:
    # 使用类属性存储，避免每次实例化都重复创建
    _POOL: List[Dict[str, str]] = [
        {"name": "物理学"},
        {"name": "化学"},
        {"name": "生物学"},
        {"name": "天文学"},
        {"name": "地球科学"},
        {"name": "经济学"},
        {"name": "心理学"},
        {"name": "社会学"},
        {"name": "法学"},
        {"name": "政治学"},
        {"name": "数学"},
        {"name": "计算机科学"},
        {"name": "历史学"},
        {"name": "哲学"},
        {"name": "艺术史"},
        {"name": "语言学"},
        {"name": "医学"},
        {"name": "工程学"},
        {"name": "考古学"}
    ]

    @classmethod
    def get_random_subjects(cls, count: int = DEFAULT_SUBJECT_COUNT) -> List[Dict[str, str]]:
        """
        从学科池中随机选择指定数量的学科。
        使用 @classmethod 因为这个方法不需要访问实例(self)状态。
        """
        # 防止请求数量超过池子总量导致崩溃
        safe_count = min(count, len(cls._POOL))
        return random.sample(cls._POOL, safe_count)

    @classmethod
    def get_subjects_formatted_prompt_segment(cls, count: int = DEFAULT_SUBJECT_COUNT) -> str:
        """
        直接生成用于 Prompt 拼接的字符串。
        """
        subjects = cls.get_random_subjects(count)
        subject_names = "、".join([s['name'] for s in subjects])
        # 格式化示例：物理学 (力学、能量)、数学 (函数、空间)
        segment = (
            f"\n【学科背景约束】：\n"
            f"请从以下学科领域中深度思考，并提取一个该领域核心的、具象的专业名词（术语）：\n"
            f">>> {subject_names} <<<\n"
            f"注意：严禁直接返回上述学科名称，必须返回该学科涵盖的具体知识点名词。"
        )
        return segment