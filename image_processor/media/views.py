from fastapi import APIRouter
from starlette import status

from image_processor.media.schema import CreateMediaSchema

router = APIRouter(
    tags=['media'],
    prefix='/media',
)

@router.post(
    "",
    response_model=CreateMediaSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_media(
        media_payload: CreateMediaSchema,
):
    return media_payload