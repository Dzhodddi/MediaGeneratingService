import logging

from image_processor.broker import Broker
from image_processor.config import get_settings
from image_processor.google_clients.google_drive_client import GoogleDriveClient
from image_processor.media.service import MediaService
from image_processor.settings.logging import configure_logging

logging.config.dictConfig(configure_logging(get_settings()))


class ServiceProvider:
    media_service: MediaService
    google_drive_client: GoogleDriveClient
    rabbitmq_broker: Broker
    logger: logging.Logger

    def __init__(self):
        cls = self.__class__
        cls.logger = logging.getLogger(__name__)
        cls.google_drive_client = GoogleDriveClient("token.json", cls.logger)
        cls.rabbitmq_broker = cls._get_broker()
        cls.media_service = cls._get_media_service()

    @classmethod
    def _get_broker(cls) -> Broker:
        return Broker(cls.logger)

    @classmethod
    def get_media_service(cls) -> MediaService:
        return cls.media_service

    @classmethod
    def _get_media_service(cls) -> MediaService:
        return MediaService(
            cls.google_drive_client,
            cls.rabbitmq_broker,
            cls.logger,
        )

    async def shutdown(self):
        await self.rabbitmq_broker.close()
        await self.google_drive_client.shutdown()
