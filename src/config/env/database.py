from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    host: str = Field(default="localhost", validation_alias="DATABASE__HOST")
    port: int = Field(default=5932, validation_alias="DATABASE__PORT")
    user: str = Field(default="guest", validation_alias="DATABASE__USER")
    password: str = Field(default="12345678", validation_alias="DATABASE__PASSWORD")
    database: str = Field(default="postgres", validation_alias="DATABASE__DATABASE")
    echo: bool = Field(default=False, validation_alias="DATABASE__ECHO")
    run_migrations: bool = Field(
        default=False, validation_alias="DATABASE__RUN_MIGRATIONS"
    )

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
