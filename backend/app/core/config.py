# 后端统一配置中枢

# lru_cache 模块提供了一个装饰器，可以将函数的结果缓存起来，以提高性能，特别适用于配置加载这种只需要加载一次的场景，避免每次调用都创建新对象，造成性能开销--只初始化一次
from functools import lru_cache
# basesettings 模块负责从环境变量加载配置，并提供全局访问接口, SettingsConfigDict 提供读取配置的规则
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 应用配置
    app_name: str = "guess-agent"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False

    # LLM 通用配置
    max_input_chars: int = 2000 # 输入文本最大字符数，超过部分将被截断
    model_timeout_seconds: int = 180 # 模型调用超时时间，单位秒
    max_retries: int = 2 # 模型调用失败重试次数

    # DeepSeek API 配置
    agent_model_api_key: str = "your_agent_model_api_key"
    agent_model_base_url: str = "https://api.siliconflow.cn/v1"
    agent_model_name: str = "deepseek-ai/DeepSeek-V3.2"
    agent_model_temperature: float = 0.3

    # 小助手模型配置
    helper_model_api_key: str = "your_helper_model_api_key"
    helper_model_base_url: str = "https://api.siliconflow.cn/v1"
    helper_model_name: str = "Qwen2.5-7B-Instruct"
    helper_model_temperature: float = 0.5

    # MongoDB 配置
    mongo_uri: str = "mongodb://root:rootpassword@mongo:27017/guess_agent?authSource=admin"
    mongo_db_name: str = "guess_agent"

    # 加密密钥（用于加密敏感数据）
    encryption_secret: str = "guess-agent-secret"
    # CORS 配置
    cors_origins: str = "*"

@lru_cache
def get_settings() -> Settings:
    return Settings()