from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx

from services.auth import AuthService
from services.jinja import templates
from services.cookies import Cookies

router = APIRouter(tags=["auth"])

@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request, success: str = None):
    data = {"request": request, "success": success, "title": "Login - Forum API Frontend"}

    if success:
        data["success"] = "Registration successful"

    return templates.TemplateResponse(
        "login.html",
        data,
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )

@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    api_url = "http://172.245.56.116:8000/auth/login"

    try:
        async with httpx.AsyncClient() as client:
            login_data = {"username": username, "password": password}

            # Make POST request to API
            response = await client.post(
                api_url,
                json=login_data,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                auth_data = response.json()
                access_token = auth_data.get("access_token")
                token_type = auth_data.get("token_type")

                if not access_token or token_type != "bearer":
                    return templates.TemplateResponse(
                        "login.html",
                        {
                            "request": request,
                            "message": "Invalid token data received",
                            "title": "Login - Forum API Frontend"
                        },
                        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
                    )

                redirect_response = RedirectResponse(url="/", status_code=303)
                Cookies.set_token_cookie(redirect_response, access_token)
                return redirect_response
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", f"Login failed: {error_data["detail"]}")
                except ValueError:
                    error_message = f"Login failed: {response.status_code}"

                return templates.TemplateResponse(
                    "login.html",
                    {
                        "request": request,
                        "message": error_message,
                        "title": "Login - Forum API Frontend"
                    },
                    headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
                )

    except httpx.RequestError as e:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "message": f"Error connecting to API: {str(e)}",
                "title": "Login - Forum API Frontend"
            },
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )

@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    return Cookies.delete_token_cookie()

@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "title": "Register - Forum API Frontend"},
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )

@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    birthdate: str = Form(...)
):
    api_url = "http://172.245.56.116:8000/auth/register"

    try:
        async with httpx.AsyncClient() as client:
            registration_data = {
                "username": username,
                "password": password,
                "email": email,
                "birthday": birthdate
            }

            response = await client.post(
                api_url,
                json=registration_data,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                return RedirectResponse(url="auth/login?success=true", status_code=303)

            try:
                error_data = response.json()
                error_message = error_data.get("message", error_data["detail"])
            except ValueError:
                error_message = f"Registration failed: {response.status_code}"

            return templates.TemplateResponse(
                "register.html",
                {
                    "request": request,
                    "message": error_message,
                    "title": "Register - Forum API Frontend"
                },
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )

    except httpx.RequestError as e:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "message": f"Error connecting to API: {str(e)}",
                "title": "Register - Forum API Frontend"
            },
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )
