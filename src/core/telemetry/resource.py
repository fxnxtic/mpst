from opentelemetry.sdk.resources import (
    DEPLOYMENT_ENVIRONMENT,
    SERVICE_NAME,
    SERVICE_VERSION,
    Resource,
)

from src.config.env import Settings, get_service_name

__all__ = ("build_resource",)


def build_resource(settings: Settings) -> Resource:
    return Resource.create(
        {
            SERVICE_NAME: get_service_name(settings),
            SERVICE_VERSION: settings.app_version,
            DEPLOYMENT_ENVIRONMENT: settings.app_env,
        }
    )
