from pathlib import Path

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from image_processor.api_router import api_router
from image_processor.config import get_settings
from image_processor.service_provider import ServiceProvider
from image_processor.errors.error_handlers import http422_error_handler, http_error_handler

BASE_DIR = Path(__file__).resolve().parent.parent


def get_application() -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            app.state.service_provider = ServiceProvider()
            yield
        finally:
            app.state.service_provider.shutdown()

    application = FastAPI(lifespan=lifespan)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_cors_origin,
        allow_credentials=settings.allowed_cors_credentials,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, http422_error_handler)
    application.include_router(api_router)

    return application


service = get_application()
