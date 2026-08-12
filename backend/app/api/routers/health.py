from fastapi import APIRouter

router = APIRouter()

@router.get("/", tags=["health"])
async def health():
    """Simple healthcheck endpoint."""
    return {"status": "ok"}
