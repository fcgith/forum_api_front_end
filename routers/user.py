from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from services.jinja import templates
import httpx


router = APIRouter(tags=["user"])

@router.get("/users/{user_id}", response_class=HTMLResponse)
async def get_user(request: Request, user_id: int):
    api_url = f"http://172.245.56.116:8000/users/{user_id}"

    try:
        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache"}
            response = await client.get(api_url, headers=headers)

            if response.status_code == 200:
                user_data = response.json()
                return templates.TemplateResponse(
                    "user.html",
                    {"request": request, "user": user_data, "title": "User Details - Forum API Frontend"},
                    headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
                )
            else:
                print(f"API returned status {response.status_code}: {response.text}")
                try:
                    if response.text:
                        error_data = response.json()
                        error_message = error_data.get("message", f"API error: {response.status_code}")
                    else:
                        error_message = f"API returned empty response with status {response.status_code}"
                except ValueError:
                    error_message = f"API error: {response.status_code} - {response.text or 'No content'}"

                return templates.TemplateResponse(
                    "error.html",
                    {"request": request, "message": error_message, "title": "Error - Forum API Frontend"},
                    headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
                )

    except httpx.RequestError as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": f"Error connecting to API: {str(e)}", "title": "Error - Forum API Frontend"},
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )