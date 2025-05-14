import httpx

from services.auth import AuthService
from services.cookies import Cookies
from services.errors import internal_error
from services.jinja import templates
from services.permissions import PermissionService


class MainService:
    def __init__(self):
        pass

    @classmethod
    async def index_page_logged_in(cls, request, user_data):
        api_url = "http://172.245.56.116:8000/categories/?token="
        token = Cookies.get_access_token_from_cookie(request)
        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache"}
            response = await client.get(f"{api_url}{token}", headers=headers)
            data = {"is_authenticated": True, "admin": True if user_data["admin"] > 0 else False}
            if response.status_code == 200:
                all_categories = response.json()

                # Filter categories based on permissions
                visible_categories = []
                for category in all_categories:
                    # Check permission for this category
                    permission_type = await PermissionService.check_category_permission(request, category["id"])
                    category_hidden = category.get("hidden", False)

                    # Check if user can view this category
                    if PermissionService.can_view_category(permission_type, category_hidden):
                        # Add permission info to the category
                        category["permission_type"] = permission_type
                        category["can_add_topic"] = PermissionService.can_add_topic(permission_type)
                        visible_categories.append(category)

                data["categories"] = visible_categories
                data["title"] = "Home/Categories - Forum API Frontend"
                data["request"] = request
                return templates.TemplateResponse(
                    "categories.html",
                    data,
                    headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
                )
            else:
                raise internal_error

    @classmethod
    async def get_main_page(cls, request):
        user_data = await AuthService.get_user_data_from_cookie(request)
        if user_data["is_authenticated"]:
            return await cls.index_page_logged_in(request, user_data)
        else:
            user_data["request"] = request
            user_data["username"] = user_data.get("username", "Error")
            user_data["admin"] = user_data.get("admin", False),
            user_data["title"] = "Home - Forum API Frontend"
            return templates.TemplateResponse(
                "index.html",
                user_data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )
