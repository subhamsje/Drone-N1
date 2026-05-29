from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "altaria-backend"}


@router.get("/ready")
async def ready():
    return {"status": "ready", "cognitive": True}
