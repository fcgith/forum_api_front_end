from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse

from services.admin import AdminService

router = APIRouter(tags=["admin"])

@router.get("/", response_class=HTMLResponse)
async def admin_panel(request: Request):
    """
    Admin panel main page.
    """
    return await AdminService.get_admin_panel(request)

@router.get("/add-category", response_class=HTMLResponse)
async def add_category_form(request: Request):
    """
    Form for adding a new category.
    """
    return await AdminService.get_add_category_form(request)

@router.post("/add-category", response_class=HTMLResponse)
async def add_category(request: Request, name: str = Form(...), description: str = Form(...)):
    """
    Add a new category.
    """
    return await AdminService.add_category(request, name, description)
