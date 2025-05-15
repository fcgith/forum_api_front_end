from fastapi import Request, Form
import httpx

from services.auth import AuthService
from services.cookies import Cookies
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
                "icon": "bi-folder-plus",
                "url": "/admin/add-category"
            },
            {
                "name": "Category Hidden Status",
                "description": "Update categories' hidden status.",
                "icon": "bi-folder",
                "url": "/admin/category-hidden-status"
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

    @classmethod
    async def get_add_category_form(cls, request):
        """
        Get the add category form page.
        """
        user_data = await cls.verify_admin(request)

        data = {
            "request": request,
            "title": "Add Category - Forum API Frontend",
            "is_authenticated": user_data["is_authenticated"],
            "admin": user_data["admin"]
        }

        return templates.TemplateResponse(
            "add_category.html",
            data,
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )

    @classmethod
    async def add_category(cls, request, name: str, description: str):
        """
        Add a new category to the forum.
        """
        # Verify that the user is an admin
        await cls.verify_admin(request)

        # Get the authentication token
        token = Cookies.get_access_token_from_cookie(request)

        # Make the API request to add the category
        async with httpx.AsyncClient() as client:
            headers = {"Content-Type": "application/json"}
            response = await client.post(
                f"http://172.245.56.116:8000/categories/add?token={token}",
                json={"name": name, "description": description},
                headers=headers
            )

            # Check if the request was successful
            if response.status_code != 200:
                # If not, return the form with an error message
                user_data = await AuthService.get_user_data_from_cookie(request)
                data = {
                    "request": request,
                    "title": "Add Category - Forum API Frontend",
                    "is_authenticated": user_data["is_authenticated"],
                    "admin": user_data["admin"],
                    "message": f"Failed to add category: {response.text}"
                }
                return templates.TemplateResponse(
                    "add_category.html",
                    data,
                    headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
                )

            # If successful, redirect back to the add-category page with a success message
            from fastapi.responses import RedirectResponse
            user_data = await AuthService.get_user_data_from_cookie(request)
            data = {
                "request": request,
                "title": "Add Category - Forum API Frontend",
                "is_authenticated": user_data["is_authenticated"],
                "admin": user_data["admin"],
                "message": "Category successfully created!",
                "success": True
            }
            return templates.TemplateResponse(
                "add_category.html",
                data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )
