from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    name: str = Field(default="modern-python-service", validation_alias="APP__NAME")
    host: str = Field(default="0.0.0.0", validation_alias="APP__HOST")
    port: int = Field(default=80, validation_alias="APP__PORT")
    version: str = Field(default="0.1.0", validation_alias="APP__VERSION")
    env: str = Field(default="development", validation_alias="APP__ENV")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class LoggingSettings(BaseSettings):
    level: str = Field(default="INFO", validation_alias="LOGGING__LEVEL")
    json_output: bool = Field(default=False, validation_alias="LOGGING_JSON_OUTPUT")
    muted_loggers: list[str] = Field(default_factory=list)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
