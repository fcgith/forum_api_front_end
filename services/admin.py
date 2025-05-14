from fastapi import Request

from services.auth import AuthService
from services.errors import not_authorized
from services.jinja import templates


class AdminService:
    @classmethod
    async def verify_admin(cls, request):
        """
        Verify that the user is an admin.
        Raises not_authorized if the user is not an admin.
        """
        user_data = await AuthService.get_user_data_from_cookie(request)
        if not user_data["is_authenticated"] or not user_data["admin"]:
            raise not_authorized
        return user_data

    @classmethod
    async def get_admin_panel(cls, request):
        """
        Get the admin panel page.
        """
        user_data = await cls.verify_admin(request)
        
        # Define admin features/subpages
        admin_features = [
            {
                "name": "Add Category",
                "description": "Add category to the forum.",
                "icon": "bi-people",
                "url": "/admin/add-category"
            }
        ]
        
        data = {
            "request": request,
            "title": "Admin Panel - Forum API Frontend",
            "admin_features": admin_features,
            "is_authenticated": user_data["is_authenticated"],
            "admin": user_data["admin"]
        }
        
        return templates.TemplateResponse(
            "admin.html",
            data,
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )