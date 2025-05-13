import httpx
from fastapi.responses import RedirectResponse

from services.cookies import Cookies
from services.errors import not_authorized
from services.jinja import templates


class AuthService:

    @classmethod
    async def get_user_data_from_cookie(cls, request) -> dict:
        access_token = Cookies.get_access_token_from_cookie(request)
        is_authenticated = access_token is not None

        data = {"is_authenticated": False, "admin": False}
        if is_authenticated:
            async with httpx.AsyncClient() as client:
                headers = {"Cache-Control": "no-cache"}
                response = await client.get(f"http://172.245.56.116:8000/auth/?token={access_token}", headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    data["is_authenticated"] = True
                    data["admin"] = True if data["admin"] > 0 else False
                return data
        return data

    @classmethod
    async def verify_logged_in(cls, request) -> dict:
        data = await cls.get_user_data_from_cookie(request)
        if data["is_authenticated"]:
            return data
        raise not_authorized

    @classmethod
    async def login_form(cls, request, success: str = None):
        data = await cls.get_user_data_from_cookie(request)
        if data.get("is_authenticated"):
            return RedirectResponse(url="/", status_code=303)

        data = {"request": request, "success": success, "title": "Login - Forum API Frontend"}

        if success:
            data["success"] = "Registration successful"

        return templates.TemplateResponse(
            "login.html",
            data,
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )

    @classmethod
    async def login_form_post(cls, request, username, password):
        data = await cls.get_user_data_from_cookie(request)
        if data["is_authenticated"]:
            return RedirectResponse(url="/", status_code=303)

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
                        error_message = error_data.get("message", f"Login failed: {error_data.get("detail")}")
                    except ValueError:
                        error_message = f"Login failed: Invalid credentials or server error."

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

    @classmethod
    async def register_form(cls, request):
        data = await cls.get_user_data_from_cookie(request)
        if data["is_authenticated"]:
            return RedirectResponse(url="/", status_code=303)

        return templates.TemplateResponse(
            "register.html",
            {"request": request, "title": "Register - Forum API Frontend"},
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )

    @classmethod
    async def register_form_post(cls, request, username, password, email, birthdate):
        data = await cls.get_user_data_from_cookie(request)
        if data["is_authenticated"]:
            return RedirectResponse(url="/", status_code=303)

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
                    return RedirectResponse(url="/auth/login?success=true", status_code=303)

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
