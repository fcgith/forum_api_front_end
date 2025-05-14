from fastapi import Request, APIRouter, Form
from fastapi.responses import HTMLResponse

from services.search import SearchService

router = APIRouter(tags=["search"])

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return await SearchService.get_main_page(request)

@router.post("/{page}", response_class=HTMLResponse)
async def search_post(request: Request, page: int, search: str = Form(""), sort: str = Form("desc")):
    return await SearchService.search(request, search, page, sort)

@router.get("/{page}", response_class=HTMLResponse)
async def search_get(request: Request, page: int, search: str = "", sort: str = "desc"):
    return await SearchService.search(request, search, page, sort)
