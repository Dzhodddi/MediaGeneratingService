import logging


class ServiceProvider:

    def __init__(self):
        cls = self.__class__


    @staticmethod
    def _get_logger() -> logging.Logger:
        return logging.getLogger(__name__)

    def shutdown(self):
        pass
