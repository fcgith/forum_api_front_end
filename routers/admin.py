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

@router.get("/category-hidden-status", response_class=HTMLResponse)
async def category_hidden_status_form(request: Request):
    """
    Form for updating a category's hidden status.
    """
    return await AdminService.get_category_hidden_status_form(request)

@router.post("/category-hidden-status", response_class=HTMLResponse)
async def update_category_hidden_status(
    request: Request, 
    category_id: int = Form(...), 
    hidden: bool = Form(False)
):
    """
    Update a category's hidden status.
    """
    return await AdminService.update_category_hidden_status(request, category_id, hidden)

@router.get("/lock-category", response_class=HTMLResponse)
async def category_lock_form(request: Request):
    """
    Form for updating a category's lock status.
    """
    return await AdminService.get_category_lock_form(request)

@router.post("/lock-category", response_class=HTMLResponse)
async def update_category_lock(
    request: Request,
    category_id: int = Form(...),

):
    """
    Lock category.
    """
    return await AdminService.update_category_lock(request, category_id)

@router.get("/lock-topic", response_class=HTMLResponse)
async def topic_lock_form(request: Request):
    """
    Form for updating a topics's lock status.
    """
    return await AdminService.get_topic_lock_form(request)

@router.post("/lock-topic", response_class=HTMLResponse)
async def update_topic_lock(
    request: Request,
    topic_id: int = Form(...),

):
    """
    Lock topic.
    """
    return await AdminService.update_topic_lock(request, topic_id)

@router.get("/update-privileges", response_class=HTMLResponse)
async def user_update_privileges_form(request: Request):
    """
    Form for updating a user's permissions.
    """
    return await AdminService.get_update_privileges_form(request)

@router.post("/update-privileges", response_class=HTMLResponse)
async def update_user_privileges(
    request: Request,
    category_id: int = Form(...),
    user_id: int = Form(...),
    permissions: int = Form(...),
):
    """
    Update user permissions
    """
    return await AdminService.update_user_privileges(request, category_id, user_id, permissions)

@router.get("/view-privilege-users",response_class=HTMLResponse)
async def view_privilege_users(request: Request):
    """
    Form for updating a user's permissions.
    """
    return await AdminService.get_view_privileged_users_form(request)

@router.post("/view-privileged-users",response_class=HTMLResponse)
async def update_view_privilege_users(
    request: Request,
    category_id: int = Form(...),
):
    """
    Update user permissions
    """
    return await AdminService.view_privileged_users(request, category_id)
