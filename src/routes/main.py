from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "CodingAgentV2 API"}

@router.get("/health")
async def health():
    return {"status": "healthy"}