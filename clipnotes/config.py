import os
from dataclasses import dataclass

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

settings = Settings()
