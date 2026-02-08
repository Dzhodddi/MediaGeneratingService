import os
from enum import Enum

from pydantic_settings import BaseSettings


class AppEnvTypes(Enum):
    local = "local"
    test = "test"
    qa = "qa"
    production = "production"


class BaseAppSettings(BaseSettings):
    env: AppEnvTypes = os.getenv("env") or AppEnvTypes.local
