import httpx
from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse

from services.auth import AuthService
from services.jinja import templates
from services.cookies import Cookies

router = APIRouter(tags=["main"])


async def index_page_logged_in(request, user_data):
    api_url = "http://172.245.56.116:8000/categories/?token="
    token = Cookies.get_access_token_from_cookie(request)
    async with httpx.AsyncClient() as client:
        headers = {"Cache-Control": "no-cache"}
        response = await client.get(f"{api_url}{token}", headers=headers)
        data = {"is_authenticated": True, "admin": False}
        if response.status_code == 200:
            data["categories"] = response.json()
            data["admin"] = True if user_data["admin"] > 0 else False
            print(data["categories"])
            return data

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    user_data = await AuthService.get_user_data_from_cookie(request)
    if user_data["is_authenticated"]:
        return index_page_logged_in(request, user_data)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "is_authenticated": user_data["is_authenticated"],
            "username": "Error" if not user_data["is_authenticated"] else user_data["username"],
            "admin": user_data.get("admin", False),
            "title": "Home - Forum API Frontend"
        },
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )