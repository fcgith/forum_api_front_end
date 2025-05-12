from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx

from services.auth import AuthService
from services.jinja import templates
from services.cookies import Cookies

router = APIRouter(tags=["auth"])

@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request, success: str = None):
    return await AuthService.login_form(request, success)

@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    return await AuthService.login_form_post(request, username, password)

@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    return Cookies.delete_token_cookie()

@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return await AuthService.register_form(request)

@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    birthdate: str = Form(...)
):
    return await AuthService.register_form_post(request, username, password, email, birthdate)