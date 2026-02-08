import asyncio

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from image_processor.api_router import api_router
from image_processor.config import get_settings
from image_processor.service_provider import ServiceProvider
from image_processor.errors.error_handlers import (
    http422_error_handler,
    http_error_handler,
)


def get_application() -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        service_provider = ServiceProvider()
        app.state.service_provider = service_provider
        await service_provider.google_drive_client.setup()
        await service_provider.rabbitmq_broker.connect()

        task = asyncio.create_task(
            service_provider.rabbitmq_broker.consume(
                service_provider.media_service.process_task
            )
        )
        try:
            yield
        finally:
            task.cancel()
            await service_provider.shutdown()

    application = FastAPI(lifespan=lifespan)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_cors_origin,
        allow_credentials=settings.allowed_cors_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, http422_error_handler)
    application.include_router(api_router)

    return application


service = get_application()
