from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "Israel News Developmental Analysis Engine",
        "version": "0.1.0",
    }
