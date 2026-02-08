from fastapi import APIRouter, Depends, status, Request

from image_processor.limiter import limiter
from image_processor.media.schema import CreateMediaSchema
from image_processor.media.service import MediaService
from image_processor.service_provider import ServiceProvider

router = APIRouter(
    tags=["media"],
)


@router.post(
    "/process-media",
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("2/minute")
async def create_media(
    request: Request,
    media_payload: CreateMediaSchema,
    media_service: MediaService = Depends(ServiceProvider.get_media_service),
):
    await media_service.save_file(media_payload)
    return {"status": "uploaded"}
