# Prompt Loader

# 导入pathlib库中的Path类，用于处理文件路径
from pathlib import Path

class PromptLoader:
    def __init__(self, prompts_dir: str):
        # 初始化PromptLoader类，接受一个字符串参数prompts_dir，表示提示词文件所在的目录
        self.prompts_dir = Path(prompts_dir)

    def load_prompt(self, prompt_name: str) -> str:
        # 加载指定名称的提示词文件，并返回其内容作为字符串
        prompt_path = self.prompts_dir / f"{prompt_name}.txt"
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file '{prompt_name}.txt' not found in '{self.prompts_dir}'")
        return prompt_path.read_text(encoding='utf-8').strip()