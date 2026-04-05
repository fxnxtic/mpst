from pydantic import Field
from pydantic_settings import BaseSettings


class OtelSettings(BaseSettings):
    enabled: bool = Field(default=False, validation_alias="OTEL__ENABLED")
    collector_url: str = Field(
        default="http://localhost:4318", validation_alias="OTEL__COLLECTOR_URL"
    )
    sample_ratio: float = Field(default=1.0, validation_alias="OTEL__SAMPLE_RATIO")
    metrics_export_interval_ms: int = Field(
        default=60_000, validation_alias="OTEL__METRICS_EXPORT_INTERVAL_MS"
    )
    excluded_urls: str = Field(default="", validation_alias="OTEL__EXCLUDED_URLS")

    @property
    def endpoint(self) -> str:
        return self.collector_url

    @property
    def insecure(self) -> bool:
        return not self.collector_url.startswith("https")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
