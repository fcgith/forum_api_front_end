import httpx
from fastapi import APIRouter, Response, Request, HTTPException
from fastapi.responses import HTMLResponse

from services.auth import AuthService
from services.cookies import Cookies
from services.errors import not_authorized
from services.jinja import templates

router = APIRouter()

@router.get("/{category}", response_class=HTMLResponse)
async def get_category(request: Request, category: int):
    token = Cookies.get_access_token_from_cookie(request)
    data = await AuthService.get_user_data_from_cookie(request)

    if not data["is_authenticated"]:
        raise not_authorized

    if data["is_authenticated"]:
        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache"}
            response_category = await client.get(f"http://172.245.56.116:8000/categories/{category}?token={token}", headers=headers)
            response_topics = await client.get(f"http://172.245.56.116:8000/categories/{category}/topics?token={token}", headers=headers)
            if response_category.status_code == 200 and response_topics.status_code == 200:
                data["topics"] = response_topics.json()
                data["category"] = response_category.json()
                data["admin"] = True if data.get("admin") > 0 else False
                data["title"] = "Category - Forum API Frontend"
                data["request"] = request
                return templates.TemplateResponse(
                    "category.html",
                    data,
                    headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
                )
            else:
                if response_category.status_code == 403 or response_topics.status_code == 403:
                    raise not_authorized

    raise HTTPException(status_code=403, detail="Not authorized")