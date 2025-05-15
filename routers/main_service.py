from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse

from services.main import MainService

router = APIRouter(tags=["main"])

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return await MainService.get_main_page(request)