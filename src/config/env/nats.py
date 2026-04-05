from pydantic import Field
from pydantic_settings import BaseSettings


class NatsSettings(BaseSettings):
    host: str = Field(default="localhost", validation_alias="NATS__HOST")
    port: int = Field(default=4222, validation_alias="NATS__PORT")
    user: str = Field(default="guest", validation_alias="NATS__USER")
    password: str = Field(default="12345678", validation_alias="NATS__PASSWORD")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def url(self) -> str:
        return f"nats://{self.user}:{self.password}@{self.host}:{self.port}"
