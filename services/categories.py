import httpx
from fastapi.responses import RedirectResponse

from services.auth import AuthService
from services.cookies import Cookies
from services.errors import not_authorized, not_found
from services.jinja import templates
from services.permissions import PermissionService


class CategoryService:
    def __init__(self):
        pass

    @classmethod
    async def get_topic_form(cls, request, category):
        token = Cookies.get_access_token_from_cookie(request)
        data = await AuthService.get_user_data_from_cookie(request)

        if not data["is_authenticated"]:
            raise not_authorized

        # Check the user's permission for this category
        permission_type = await PermissionService.check_category_permission(request, category)

        # Get category details to check if it's hidden
        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache"}
            response_category = await client.get(f"http://172.245.56.116:8000/categories/{category}?token={token}", headers=headers)

            if response_category.status_code == 404:
                raise not_found

            if response_category.status_code != 200:
                raise not_authorized

            category_data = response_category.json()
            category_hidden = category_data.get("hidden", False)

            # Check if the user can add a topic
            if not PermissionService.can_add_topic(permission_type, category_hidden):
                raise not_authorized

            # Check if the user can view this category
            if not PermissionService.can_view_category(permission_type, category_hidden):
                raise not_authorized

            data["category"] = category_data
            data["admin"] = True if data.get("admin") > 0 else False
            data["title"] = "Add Topic - Forum API Frontend"
            data["request"] = request
            data["permission_type"] = permission_type

            return templates.TemplateResponse(
                "addtopic.html",
                data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )

    @classmethod
    async def get_category_by_id(cls, request, category):
        token = Cookies.get_access_token_from_cookie(request)
        data = await AuthService.get_user_data_from_cookie(request)

        if not data["is_authenticated"]:
            raise not_authorized

        # Check the user's permission for this category
        permission_type = await PermissionService.check_category_permission(request, category)

        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache"}
            response_category = await client.get(f"http://172.245.56.116:8000/categories/{category}?token={token}",
                                                 headers=headers)

            if response_category.status_code == 404:
                raise not_found

            if response_category.status_code != 200:
                raise not_authorized

            category_data = response_category.json()
            category_hidden = category_data.get("hidden", False)

            # Check if the user can view this category
            if not PermissionService.can_view_category(permission_type, category_hidden):
                raise not_authorized

            # If the user can view the category, get the topics
            response_topics = await client.get(
                f"http://172.245.56.116:8000/categories/{category}/topics?token={token}", headers=headers)

            if response_topics.status_code != 200:
                raise not_authorized

            data["topics"] = response_topics.json()
            data["category"] = category_data
            data["admin"] = True if data.get("admin") > 0 else False
            data["title"] = "Category - Forum API Frontend"
            data["request"] = request
            data["permission_type"] = permission_type
            data["can_add_topic"] = PermissionService.can_add_topic(permission_type, category_hidden)

            return templates.TemplateResponse(
                "category.html",
                data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )

    @classmethod
    async def topic_form_post(cls, request, category_id: int):
        token = Cookies.get_access_token_from_cookie(request)
        data = await AuthService.get_user_data_from_cookie(request)

        if not data["is_authenticated"]:
            raise not_authorized

        # Check the user's permission for this category
        permission_type = await PermissionService.check_category_permission(request, category_id)

        # Get category details to check if it's hidden
        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache", "Authorization": token}
            response_category = await client.get(f"http://172.245.56.116:8000/categories/{category_id}", headers=headers)

            if response_category.status_code == 404:
                raise not_found

            if response_category.status_code != 200:
                raise not_authorized

            category_data = response_category.json()
            category_hidden = category_data.get("hidden", False)

            # Check if the user can add a topic
            if not PermissionService.can_add_topic(permission_type, category_hidden):
                raise not_authorized

        form_data = await request.form()
        name = form_data.get("name")
        content = form_data.get("content")

        if not name or not content:
            # Return to the form with an error message if required fields are missing
            # Get the category details to maintain consistency with get_topic_form
            async with httpx.AsyncClient() as client:
                headers = {"Cache-Control": "no-cache", "Authorization": token}
                response_category = await client.get(f"http://172.245.56.116:8000/categories/{category_id}",
                                                    headers=headers)

                if response_category.status_code == 404:
                    raise not_found

                if response_category.status_code != 200:
                    raise not_authorized

                category_data = response_category.json()
                category_hidden = category_data.get("hidden", False)

                # Check if the user can view this category
                if not PermissionService.can_view_category(permission_type, category_hidden):
                    raise not_authorized

                data["category"] = category_data

            data["message"] = "Topic title and content are required."
            data["request"] = request
            data["title"] = "Add Topic - Forum API Frontend"
            data["permission_type"] = permission_type
            return templates.TemplateResponse(
                "addtopic.html",
                data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )

        try:
            # Double-check permissions before posting
            permission_type = await PermissionService.check_category_permission(request, category_id)

            async with httpx.AsyncClient() as check_client:
                # Get category details to check if it's hidden
                response_category = await check_client.get(f"http://172.245.56.116:8000/categories/{category_id}",
                                                           headers={"Cache-Control": "no-cache", "Authorization": token})

                if response_category.status_code == 404:
                    raise not_found

                if response_category.status_code != 200:
                    raise not_authorized

                category_data = response_category.json()
                category_hidden = category_data.get("hidden", False)

                if not PermissionService.can_add_topic(permission_type, category_hidden):
                    raise not_authorized

            async with httpx.AsyncClient() as client:
                # Convert newlines to <br /> tags
                content_with_br = content.replace('\n', '<br />')

                topic_data = {
                    "name": name,
                    "content": content_with_br,
                    "category_id": category_id
                }

                response = await client.post(
                    f"http://172.245.56.116:8000/topics/?token={token}",
                    json=topic_data,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 200 or response.status_code == 201:
                    # Parse the API response to get the topic_id
                    response_data = response.json()
                    topic_id = response_data.get("topic_id")

                    # Redirect to the topic page with success message
                    return RedirectResponse(url=f"/topics/{topic_id}?success=true", status_code=303)

                # Handle error response
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", error_data.get("detail", f"Error creating topic: {response.status_code}"))
                except ValueError:
                    error_message = f"Error creating topic: {response.status_code}"

                # Return to the form with the error message
                # Get the category details to maintain consistency with get_topic_form
                response_category = await client.get(f"http://172.245.56.116:8000/categories/{category_id}",
                                                     headers={"Cache-Control": "no-cache", "Authorization": token}
                                                     )

                if response_category.status_code == 404:
                    raise not_found

                if response_category.status_code != 200:
                    raise not_authorized

                category_data = response_category.json()
                category_hidden = category_data.get("hidden", False)

                # Check if the user can view this category
                if not PermissionService.can_view_category(permission_type, category_hidden):
                    raise not_authorized

                data["category"] = category_data
                data["permission_type"] = permission_type
                data["message"] = error_message
                data["request"] = request
                data["title"] = "Add Topic - Forum API Frontend"
                return templates.TemplateResponse(
                    "addtopic.html",
                    data,
                    headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
                )

        except httpx.RequestError as e:
            # Handle connection errors
            # Get the category details to maintain consistency with get_topic_form
            try:
                # Double-check permissions
                permission_type = await PermissionService.check_category_permission(request, category_id)

                async with httpx.AsyncClient() as client:
                    headers = {"Cache-Control": "no-cache", "Authorization": token}
                    response_category = await client.get(f"http://172.245.56.116:8000/categories/{category_id}",
                                                         headers=headers)

                    if response_category.status_code == 404:
                        raise not_found

                    if response_category.status_code != 200:
                        raise not_authorized

                    category_data = response_category.json()
                    category_hidden = category_data.get("hidden", False)

                    # Check if the user can view this category
                    if not PermissionService.can_view_category(permission_type, category_hidden):
                        raise not_authorized

                    data["category"] = category_data
                    data["permission_type"] = permission_type
            except (httpx.RequestError, not_authorized, not_found):
                # If we can't get the category or don't have permission, we'll just continue without it
                pass

            data["message"] = f"Error connecting to API: {str(e)}"
            data["request"] = request
            data["title"] = "Add Topic - Forum API Frontend"
            return templates.TemplateResponse(
                "addtopic.html",
                data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )
