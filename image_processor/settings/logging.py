from image_processor.settings.app import AppSettings


def configure_logging(settings: AppSettings):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "basic": {
                "format": settings.LOG_FORMAT_DEBUG,
            }
        },
        "handlers": {
            "console": {
                "formatter": "basic",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
                "level": settings.LOG_LEVEL,
            }
        },
        "loggers": {
            "uvicorn.asgi": {"handlers": ["console"], "level": settings.LOG_LEVEL},
            "uvicorn.access": {"handlers": ["console"], "level": settings.LOG_LEVEL},
            "": {"handlers": ["console"], "level": settings.LOG_LEVEL},
        },
    }
