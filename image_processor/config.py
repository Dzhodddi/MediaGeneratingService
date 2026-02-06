from functools import lru_cache
from typing import Dict, Type

from image_processor.settings.app import AppSettings
from image_processor.settings.base import AppEnvTypes, BaseAppSettings
from image_processor.settings.local import LocalAppSettings
from image_processor.settings.test import TestAppSettings
from image_processor.settings.qa import QAAppSettings
from image_processor.settings.production import ProductionAppSettings


environments: Dict[AppEnvTypes, Type[AppSettings]] = {
    AppEnvTypes.local: LocalAppSettings,
    AppEnvTypes.test: TestAppSettings,
    AppEnvTypes.qa: QAAppSettings,
    AppEnvTypes.production: ProductionAppSettings,
}


@lru_cache
def get_settings() -> AppSettings:
    app_env = BaseAppSettings().env
    config = environments[app_env]
    return config()
