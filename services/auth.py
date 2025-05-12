import httpx

from services.cookies import Cookies


class AuthService:

    @classmethod
    async def get_user_data_from_cookie(cls, request):
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

    @classmethod
    async def verify_logged_in(cls, request) -> bool:
        with await AuthService.get_user_data_from_cookie(request) as data:
            if data["is_authenticated"]:
                return False
        return True