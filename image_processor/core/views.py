from fastapi import APIRouter

router = APIRouter(
    prefix='',
    tags=["health"]

)


@router.get('/health', name='health')
async def root():
    return {'status': "ok"}
