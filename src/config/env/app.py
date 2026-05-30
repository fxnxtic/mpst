from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    name: str = Field(default="modern-python-service", validation_alias="APP__NAME")
    host: str = Field(default="0.0.0.0", validation_alias="APP__HOST")
    port: int = Field(default=80, validation_alias="APP__PORT")
    version: str = Field(default="0.1.0", validation_alias="APP__VERSION")
    env: str = Field(default="development", validation_alias="APP__ENV")


class LoggingSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    level: str = Field(default="INFO", validation_alias="LOGGING__LEVEL")
    json_output: bool = Field(default=False, validation_alias="LOGGING__JSON_OUTPUT")
    muted_loggers: list[str] = Field(default_factory=list)
