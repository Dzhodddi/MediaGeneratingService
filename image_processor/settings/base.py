import os
from enum import Enum

from pydantic_settings import BaseSettings


class AppEnvTypes(Enum):
    local: str = 'local'
    test: str = 'test'
    qa: str = 'qa'
    production: str = 'production'


class BaseAppSettings(BaseSettings):
    env: AppEnvTypes = os.getenv('env') or AppEnvTypes.local
