from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from services.jinja import templates
from services.user import UserService
import httpx


router = APIRouter(tags=["user"])

@router.get("/me", response_class=HTMLResponse)
async def get_profile(request: Request):
    """
    Get the profile page for the currently logged-in user.
    """
    return await UserService.get_user_profile(request)

@router.get("/profile/avatar", response_class=HTMLResponse)
async def get_avatar_change_page(request: Request):
    """
    Get the avatar change page.
    """
    return await UserService.get_avatar_change_page(request)

@router.post("/profile/avatar", response_class=HTMLResponse)
async def update_avatar(request: Request):
    """
    Process the avatar update form submission.
    """
    return await UserService.update_avatar(request)

@router.get("/{user_id}", response_class=HTMLResponse)
async def get_user(request: Request, user_id: int):
    """
    Get the profile page for a specific user by ID.
    """
    return await UserService.get_user_by_id(request, user_id)
