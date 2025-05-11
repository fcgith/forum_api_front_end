from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_categories():
    return {"categories": ["food", "travel", "sports"]}