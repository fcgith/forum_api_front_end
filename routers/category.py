import httpx
from fastapi import APIRouter, Response, Request, HTTPException
from fastapi.responses import HTMLResponse

from services.auth import AuthService
from services.cookies import Cookies
from services.jinja import templates

router = APIRouter()

@router.get("/{category}", response_class=HTMLResponse)
async def get_category(request: Request, category: int):
    token = Cookies.get_access_token_from_cookie(request)
    user_data = await AuthService.get_user_data_from_cookie(request)

    if not user_data["is_authenticated"]:
        return HTTPException(status_code=403, detail="Not authorized")

    if user_data["is_authenticated"]:
        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache"}
            response_category = await client.get(f"http://172.245.56.116:8000/categories/{category}?token={token}", headers=headers)
            response_topics = await client.get(f"http://172.245.56.116:8000/categories/{category}/topics?token={token}", headers=headers)
            if response_category.status_code == 200 and response_topics.status_code == 200:
                return templates.TemplateResponse(
                    "category.html",
                    {
                        "request": request,
                         "topics": response_topics.json(),
                         "category": response_category.json(),
                         "is_authenticated": user_data["is_authenticated"],
                         "admin": user_data["admin"],
                         "title": "Category - Forum API Frontend"
                     },
                    headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
                )
            else:
                raise HTTPException(status_code=500, detail="Error fetching topics")
    return HTTPException(status_code=403, detail="Not authorized")