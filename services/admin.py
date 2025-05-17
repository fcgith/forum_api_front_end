from fastapi import Request, Form
import httpx

from services.auth import AuthService
from services.cookies import Cookies
from services.errors import not_authorized, not_found
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
                "icon": "bi-plus-circle",
                "url": "/admin/add-category"
            },
            {
                "name": "Category Hidden Status",
                "description": "Update categories' hidden status.",
                "icon": "bi-eye-slash",
                "url": "/admin/category-hidden-status"
            },
            {
                "name": "Lock Category",
                "description": "Lock category from the forum.",
                "icon": "bi-shield-lock",
                "url": "/admin/lock-category"
            },
            {
                "name": "Lock Topic",
                "description": "Lock topic from the forum.",
                "icon": "bi-lock",
                "url": "/admin/lock-topic"
            },
            {
                "name": "Update User Category Privileges",
                "description": "Set the access level of users to a category.",
                "icon": "bi-person-gear",
                "url": "/admin/update-privileges"
            },
            {
                "name": "View Privileged Users",
                "description": "View users with access to a private category",
                "icon": "bi-person-check",
                "url": "/admin/view-privilege-users"
            }
        ]

        data = user_data | {
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

        data = user_data | {
            "request": request,
            "title": "Add Category - Forum API Frontend",
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
        user_data = await cls.verify_admin(request)

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
                data = user_data | {
                    "request": request,
                    "title": "Add Category - Forum API Frontend",
                    "message": f"Failed to add category: {response.text}"
                }
                return templates.TemplateResponse(
                    "add_category.html",
                    data,
                    headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
                )

            user_data = await AuthService.get_user_data_from_cookie(request)
            data = user_data | {
                "request": request,
                "title": "Add Category - Forum API Frontend",
                "message": "Category successfully created!",
                "success": True
            }
            return templates.TemplateResponse(
                "add_category.html",
                data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )

    @classmethod
    async def get_category_hidden_status_form(cls, request):
        """
        Get the category hidden status form page.
        """
        user_data = await cls.verify_admin(request)

        # Get the authentication token
        token = Cookies.get_access_token_from_cookie(request)

        # Fetch all categories from the API
        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache", "Authorization": token}
            response = await client.get(
                f"http://172.245.56.116:8000/categories/",
                headers=headers
            )

            if response.status_code != 200:
                raise not_authorized

            categories = response.json()

            data = user_data | {
                "request": request,
                "title": "Category Hidden Status - Forum API Frontend",
                "categories": categories
            }

            return templates.TemplateResponse(
                "category_hidden_status.html",
                data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )

    @classmethod
    async def update_category_hidden_status(cls, request, category_id: int, hidden: bool = False):
        """
        Update a category's hidden status.
        """
        # Verify that the user is an admin
        await cls.verify_admin(request)

        # Get the authentication token
        token = Cookies.get_access_token_from_cookie(request)

        # Convert hidden to 0 or 1
        hidden_value = 1 if hidden else 0

        # Make the API request to update the category's hidden status
        async with httpx.AsyncClient() as client:
            headers = {"Content-Type": "application/json", "Authorization": token}
            response = await client.put(
                f"http://172.245.56.116:8000/categories/hide-status",
                json={"category_id": category_id, "hidden": hidden_value},
                headers=headers
            )

            # Fetch all categories again to display the updated list
            categories_response = await client.get(
                f"http://172.245.56.116:8000/categories/",
                headers={"Cache-Control": "no-cache"}
            )

            if categories_response.status_code != 200:
                raise not_authorized

            categories = categories_response.json()
            user_data = await AuthService.get_user_data_from_cookie(request)

            # Check if the update request was successful
            if response.status_code != 200:
                # If not, return the form with an error message
                data = user_data | {
                    "request": request,
                    "title": "Category Hidden Status - Forum API Frontend",
                    "categories": categories,
                    "message": f"Failed to update category hidden status: {response.text}"
                }
                return templates.TemplateResponse(
                    "category_hidden_status.html",
                    data,
                    headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
                )

            # If successful, return the form with a success message
            data = user_data | {
                "request": request,
                "title": "Category Hidden Status - Forum API Frontend",
                "categories": categories,
                "message": "Category hidden status successfully updated!",
                "success": True
            }
            return templates.TemplateResponse(
                "category_hidden_status.html",
                data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )

    @classmethod
    async def get_category_lock_form(cls, request):
        """
        Get the category lock form page.
        """
        user_data = await cls.verify_admin(request)

        # Get the authentication token
        token = Cookies.get_access_token_from_cookie(request)

        # Fetch all categories from the API
        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache", "Authorization": token}
            response = await client.get(
                f"http://172.245.56.116:8000/categories/",
                headers=headers
            )

            if response.status_code != 200:
                raise not_authorized

            categories = response.json()

            data = user_data | {
                "request": request,
                "title": "Lock Category - Forum API Frontend",
                "categories": categories
            }

            return templates.TemplateResponse(
                "category_lock.html",
                data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )

    @classmethod
    async def update_category_lock(cls, request, category_id: int):
        """
        Lock a category.
        """
        # Verify that the user is an admin
        await cls.verify_admin(request)

        # Get the authentication token
        token = Cookies.get_access_token_from_cookie(request)

        # Make the API request to lock the category
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"http://172.245.56.116:8000/categories/{category_id}/lock?token={token}"
            )

            # Fetch all categories again to display the updated list
            categories_response = await client.get(
                f"http://172.245.56.116:8000/categories/",
                headers={"Cache-Control": "no-cache", "Authorization": token}
            )

            if categories_response.status_code != 200:
                raise not_authorized

            categories = categories_response.json()
            user_data = await AuthService.get_user_data_from_cookie(request)

            # Check if the update request was successful
            if response.status_code != 200:
                # If not, return the form with an error message
                data = user_data | {
                    "request": request,
                    "title": "Lock Category - Forum API Frontend",
                    "categories": categories,
                    "message": f"Failed to lock category: {response.text}"
                }
                return templates.TemplateResponse(
                    "category_lock.html",
                    data,
                    headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
                )

            # If successful, return the form with a success message
            data = user_data | {
                "request": request,
                "title": "Lock Category - Forum API Frontend",
                "categories": categories,
                "message": "Category successfully locked!",
                "success": True
            }
            return templates.TemplateResponse(
                "category_lock.html",
                data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )

    @classmethod
    async def get_topic_lock_form(cls, request):
        """
        Get the topic lock form page.
        """
        user_data = await cls.verify_admin(request)

        data = user_data | {
            "request": request,
            "title": "Lock Topic - Forum API Frontend",
        }

        return templates.TemplateResponse(
            "topic_lock.html",
            data,
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )

    @classmethod
    async def update_topic_lock(cls, request, topic_id: int):
        """
        Lock a topic.
        """
        # Verify that the user is an admin
        await cls.verify_admin(request)

        # Get the authentication token
        token = Cookies.get_access_token_from_cookie(request)

        # Make the API request to lock the topic
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"http://172.245.56.116:8000/topics/{topic_id}/lock?token={token}"
            )

            user_data = await AuthService.get_user_data_from_cookie(request)

            # Check if the update request was successful
            if response.status_code != 200:
                # If not, return the form with an error message
                data = user_data | {
                    "request": request,
                    "title": "Lock Topic - Forum API Frontend",
                    "message": f"Failed to lock topic: {response.text}"
                }
                return templates.TemplateResponse(
                    "topic_lock.html",
                    data,
                    headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
                )

            # If successful, return the form with a success message
            data = user_data | {
                "request": request,
                "title": "Lock Topic - Forum API Frontend",
                "message": "Topic successfully locked!",
                "success": True
            }
            return templates.TemplateResponse(
                "topic_lock.html",
                data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )

    @classmethod
    async def get_update_privileges_form(cls, request):
        """
        Get the update user privileges form page.
        """
        user_data = await cls.verify_admin(request)

        # Get the authentication token
        token = Cookies.get_access_token_from_cookie(request)

        # Fetch all categories from the API
        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache", "Authorization": token}
            response = await client.get(
                f"http://172.245.56.116:8000/categories/",
                headers=headers
            )

            if response.status_code != 200:
                raise not_authorized

            categories = response.json()

            data = user_data | {
                "request": request,
                "title": "Update User Category Privileges - Forum API Frontend",
                "categories": categories
            }

            return templates.TemplateResponse(
                "update_privileges.html",
                data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )

    @classmethod
    async def update_user_privileges(cls, request, category_id: int, user_id: int, permissions: int):
        """
        Update a user's permissions for a category.
        """
        # Verify that the user is an admin
        await cls.verify_admin(request)

        # Get the authentication token
        token = Cookies.get_access_token_from_cookie(request)

        # Make the API request to update user permissions
        async with httpx.AsyncClient() as client:
            headers = {"Content-Type": "application/json", "Authorization": token}
            response = await client.put(
                f"http://172.245.56.116:8000/categories/user-permissions",
                json={"category_id": category_id, "user_id": user_id, "permission": permissions},
                headers=headers
            )

            # Fetch all categories again to display the updated list
            categories_response = await client.get(
                f"http://172.245.56.116:8000/categories/",
                headers={"Cache-Control": "no-cache", "Authorization": token}
            )

            if categories_response.status_code != 200:
                raise not_authorized

            categories = categories_response.json()
            user_data = await AuthService.get_user_data_from_cookie(request)

            # Check if the update request was successful
            if response.status_code != 200:
                # If not, return the form with an error message
                data = user_data | {
                    "request": request,
                    "title": "Update User Category Privileges - Forum API Frontend",
                    "categories": categories,
                    "message": f"Failed to update user permissions: {response.text}"
                }
                return templates.TemplateResponse(
                    "update_privileges.html",
                    data,
                    headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
                )

            # If successful, return the form with a success message
            data = user_data | {
                "request": request,
                "title": "Update User Category Privileges - Forum API Frontend",
                "categories": categories,
                "message": "User permissions successfully updated!",
                "success": True
            }
            return templates.TemplateResponse(
                "update_privileges.html",
                data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )

    @classmethod
    async def get_view_privileged_users_form(cls, request):
        user_data = await cls.verify_admin(request)
        token = Cookies.get_access_token_from_cookie(request)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://172.245.56.116:8000/categories/",
                headers={"Cache-Control": "no-cache", "Authorization": token}
            )
            if response.status_code != 200:
                raise not_authorized
            categories = response.json()
            data = user_data | {
                "request": request,
                "title": "View Privileged Users - Forum API Frontend",
                "categories": categories
            }
            return templates.TemplateResponse(
                "view_privileged_users_form.html",
                data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )

    @classmethod
    async def view_privileged_users(cls, request, category_id: int):
        user_data = await cls.verify_admin(request)
        token = Cookies.get_access_token_from_cookie(request)
        async with httpx.AsyncClient() as client:
            # Get categories for the dropdown
            categories_response = await client.get(
                f"http://172.245.56.116:8000/categories/",
                headers={"Cache-Control": "no-cache", "Authorization": token}
            )
            if categories_response.status_code != 200:
                raise not_authorized
            categories = categories_response.json()
            # Get privileged users for the selected category
            response = await client.get(
                f"http://172.245.56.116:8000/categories/{category_id}/privileged-users",
                headers={"Cache-Control": "no-cache", "Authorization": token}
            )
            privileged_users = []
            if response.status_code == 200:
                privileged_users = response.json()
            # Permission mapping
            permission_map = {
                0: "No Access",
                1: "Normal Access",
                2: "Read-Only Access",
                3: "Write Access"
            }
            for entry in privileged_users:
                entry["permission_text"] = permission_map.get(entry["permission"], str(entry["permission"]))
            data = user_data | {
                "request": request,
                "title": "View Privileged Users - Forum API Frontend",
                "categories": categories,
                "selected_category_id": category_id,
                "privileged_users": privileged_users
            }
            return templates.TemplateResponse(
                "view_privileged_users_result.html",
                data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )
