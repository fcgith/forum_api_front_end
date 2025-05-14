from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse

from services.search import SearchService

router = APIRouter(tags=["search"])

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return await SearchService.get_main_page(request)

@router.post("/search/{page}", response_class=HTMLResponse)
async def search(request: Request, page: int, query: str="", sort: str="desc"):
    return await SearchService.search(request, query, page, sort)