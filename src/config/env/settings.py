from .app import AppSettings, LoggingSettings
from .database import DatabaseSettings
from .nats import NatsSettings
from .otel import OtelSettings


class Settings:
    def __init__(
        self,
        app: AppSettings,
        logging: LoggingSettings,
        database: DatabaseSettings,
        nats: NatsSettings,
        otel: OtelSettings,
    ) -> None:
        self.app = app
        self.logging = logging
        self.database = database
        self.nats = nats
        self.otel = otel

    @property
    def app_name(self) -> str:
        return self.app.name

    @property
    def app_version(self) -> str:
        return self.app.version

    @property
    def app_env(self) -> str:
        return self.app.env


def get_service_name(settings: Settings) -> str:
    return settings.app_name


def create_settings() -> Settings:
    return Settings(
        app=AppSettings(),
        logging=LoggingSettings(),
        database=DatabaseSettings(),
        nats=NatsSettings(),
        otel=OtelSettings(),
    )


cfg = create_settings()
