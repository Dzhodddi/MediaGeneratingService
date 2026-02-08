from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from image_processor.core.views import router as health_router
from image_processor.media.views import router as media_router


class ErrorResponse(BaseModel):
    errors: list[str] | None


api_router = APIRouter(
    default_response_class=JSONResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)

api_router.include_router(health_router)
api_router.include_router(media_router)
