import httpx

from services.auth import AuthService
from services.cookies import Cookies
from services.errors import not_authorized
from services.jinja import templates


class CategoryService:
    def __init__(self):
        pass

    @classmethod
    async def get_topic_form(cls, request, category):
        token = Cookies.get_access_token_from_cookie(request)
        data = await AuthService.get_user_data_from_cookie(request)

        if not data["is_authenticated"]:
            raise not_authorized

        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache"}
            response_category = await client.get(f"http://172.245.56.116:8000/categories/{category}?token={token}", headers=headers)
            if response_category.status_code == 200:
                data["category"] = response_category.json()
                data["admin"] = True if data.get("admin") > 0 else False
                data["title"] = "Add Topic - Forum API Frontend"
                data["request"] = request

                return templates.TemplateResponse(
                    "addtopic.html",
                    data,
                    headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
                )
            else:
                raise not_authorized

    @classmethod
    async def get_category_by_id(cls, request, category):
        token = Cookies.get_access_token_from_cookie(request)
        data = await AuthService.get_user_data_from_cookie(request)

        if data["is_authenticated"]:
            async with httpx.AsyncClient() as client:
                headers = {"Cache-Control": "no-cache"}
                response_category = await client.get(f"http://172.245.56.116:8000/categories/{category}?token={token}",
                                                     headers=headers)
                response_topics = await client.get(
                    f"http://172.245.56.116:8000/categories/{category}/topics?token={token}", headers=headers)
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

        raise not_authorized