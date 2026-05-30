from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class NatsSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    host: str = Field(default="localhost", validation_alias="NATS__HOST")
    port: int = Field(default=4222, validation_alias="NATS__PORT")
    user: str = Field(default="guest", validation_alias="NATS__USER")
    password: str = Field(default="12345678", validation_alias="NATS__PASSWORD")

    @property
    def url(self) -> str:
        return f"nats://{self.user}:{self.password}@{self.host}:{self.port}"
