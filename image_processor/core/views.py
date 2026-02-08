from fastapi import APIRouter, Request

from image_processor.limiter import limiter

router = APIRouter(prefix="", tags=["health"])


@router.get("/health", name="health")
@limiter.limit("10/minute")
async def root(request: Request):
    return {"status": "ok"}
