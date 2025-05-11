import httpx
from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse

from services.jinja import templates
from services.cookies import Cookies

router = APIRouter(tags=["main"])

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    access_token = Cookies.get_access_token_from_cookie(request)
    is_authenticated = access_token is not None

    username = "ERROR"

    if is_authenticated:
        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache"}
            response = await client.get(f"http://172.245.56.116:8000/auth/?token={access_token}", headers=headers)

            if response.status_code == 200:
                username = response.json()["username"]
                is_admin = True if response.json()["admin"] else False

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "is_authenticated": is_authenticated,
            "is_admin": True,
            "username": username,
            "title": "Home - Forum API Frontend"
        },
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )