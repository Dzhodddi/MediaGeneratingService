import logging

from image_processor.google_clients.google_drive_client import GoogleDriveClient
from image_processor.media.service import MediaService


class ServiceProvider:
    media_service: MediaService
    google_drive_client: GoogleDriveClient

    def __init__(self):
        cls = self.__class__
        cls.google_drive_client = GoogleDriveClient("token.json")
        cls.media_service = cls._get_media_service()

    @staticmethod
    def _get_logger() -> logging.Logger:
        return logging.getLogger(__name__)

    @classmethod
    def get_media_service(cls) -> MediaService:
        return cls.media_service

    @classmethod
    def _get_media_service(cls) -> MediaService:
        return MediaService(
            cls.google_drive_client
        )

    def shutdown(self):
        pass
