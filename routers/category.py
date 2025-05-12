from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from services.categories import CategoryService

router = APIRouter()

@router.get("/{category}", response_class=HTMLResponse)
async def get_category(request: Request, category: int):
    return await CategoryService.get_category_by_id(request, category)

@router.get("/{category}/new-topic", response_class=HTMLResponse)
async def get_topic(request: Request, category: int):
    return await CategoryService.get_topic_form(request, category)

@router.post("/{category}/new-topic", response_class=HTMLResponse)
async def get_topic_post(request: Request, category: int):
    return await CategoryService.get_topic_form_post(request, category)