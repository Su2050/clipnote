import os
import logging
from logging.handlers import RotatingFileHandler
from dataclasses import dataclass
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_file: str = "clipnotes.log"):
    """配置日志系统"""
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / log_file
    
    # 配置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器（轮转，最大 10MB，保留 5 个备份）
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # 避免重复日志
    logging.getLogger("uvicorn").propagate = False
    logging.getLogger("uvicorn.access").propagate = False
    
    return root_logger

@dataclass
class Settings:
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    log_level: str = os.getenv("LOG_LEVEL", "info")

    api_tokens: list[str] = tuple(
        t.strip() for t in os.getenv("API_TOKENS", "dev-token-please-change").split(",") if t.strip()
    )

    default_tenant: str = os.getenv("DEFAULT_TENANT", "localdev")

    storage_provider: str = os.getenv("STORAGE_PROVIDER", "local")
    data_dir: str = os.getenv("DATA_DIR", "./data")

    aliyun_oss_endpoint: str = os.getenv("ALIYUN_OSS_ENDPOINT", "")
    aliyun_oss_ak: str = os.getenv("ALIYUN_OSS_ACCESS_KEY_ID", "")
    aliyun_oss_sk: str = os.getenv("ALIYUN_OSS_ACCESS_KEY_SECRET", "")
    aliyun_oss_bucket: str = os.getenv("ALIYUN_OSS_BUCKET", "")
    aliyun_oss_prefix: str = os.getenv("ALIYUN_OSS_PREFIX", "clipnotes/")

    mcp_server_name: str = os.getenv("MCP_SERVER_NAME", "clipnotes-mcp")
    mcp_stateless_http: bool = os.getenv("MCP_STATELESS_HTTP", "true").lower() == "true"
    
    # MCP Server API 配置
    notes_api_url: str = os.getenv("NOTES_API_URL", "http://localhost:8000")
    notes_api_token: str = os.getenv("NOTES_API_TOKEN", "")
    
    # CORS 配置
    cors_origins: list[str] = tuple(
        origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",") if origin.strip()
    ) if os.getenv("CORS_ORIGINS") else ["*"]

settings = Settings()

# 设置默认的 notes_api_token（如果未设置）
if not settings.notes_api_token:
    settings.notes_api_token = settings.api_tokens[0] if settings.api_tokens else "dev-token-please-change"

# 初始化日志系统
setup_logging(settings.log_level)
