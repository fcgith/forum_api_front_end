import httpx
from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse

from services.jinja import templates
from services.cookies import Cookies

router = APIRouter(tags=["main"])


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    user_data = AuthService.get_user_data_from_cookie(request)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "is_authenticated": user_data["is_authenticated"],
            "username": "Error" if not user_data["is_authenticated"] else user_data["username"],
            "admin": user_data["admin"],
            "title": "Home - Forum API Frontend"
        },
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )