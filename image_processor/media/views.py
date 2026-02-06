from fastapi import APIRouter, Depends, status

from image_processor.media.schema import CreateMediaSchema
from image_processor.media.service import MediaService
from image_processor.service_provider import ServiceProvider

router = APIRouter(
    tags=['media'],
)

@router.post(
    "/process-media",
    # response_model=CreateMediaSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_media(
        media_payload: CreateMediaSchema,
        media_service: MediaService = Depends(ServiceProvider.get_media_service),
):
    await media_service.save_file(media_payload)
    return {'status':'uploaded'}
