from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from services.admin import AdminService

router = APIRouter(tags=["admin"])

@router.get("/", response_class=HTMLResponse)
async def admin_panel(request: Request):
    """
    Admin panel main page.
    """
    return await AdminService.get_admin_panel(request)
