import httpx
from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse

from services.auth import AuthService
from services.errors import not_authorized, internal_error, not_found
from services.jinja import templates
from services.cookies import Cookies
from services.permissions import PermissionService

class TopicService:
    @classmethod
    async def get_topic(cls, request: Request, topic_id: int, success: str = None):

        # Get authentication status
        token = Cookies.get_access_token_from_cookie(request)
        data = await AuthService.verify_logged_in(request)
        data["request"] = request
        data["title"] = "Topic - Forum API Frontend"

        if success:
            data["success"] = "Topic created successfully"

        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        async with httpx.AsyncClient() as client:
            # Get topic details
            response_topic = await client.get(
                f"http://172.245.56.116:8000/topics/{topic_id}?token={token}", headers=headers)

            if response_topic.status_code == 404:
                raise not_found

            if response_topic.status_code != 200:
                raise not_authorized

            topic_data = response_topic.json()
            category_id = topic_data.get("category_id")

            # Check the user's permission for this category
            permission_type = await PermissionService.check_category_permission(request, category_id)

            # Get category details to check if it's hidden
            response_category = await client.get(
                f"http://172.245.56.116:8000/categories/{category_id}?token={token}", headers=headers)

            if response_category.status_code == 404:
                raise not_found

            if response_category.status_code != 200:
                raise not_authorized

            category_data = response_category.json()
            category_hidden = category_data.get("hidden", False)

            # Check if the user can view this category and its topics
            if not PermissionService.can_view_topics(permission_type, category_hidden):
                raise not_authorized

            # Get replies for the topic
            response_replies = await client.get(
                f"http://172.245.56.116:8000/topics/{topic_id}/replies?token={token}", headers=headers)

            if response_replies.status_code != 200:
                raise not_authorized

            data["topic"] = topic_data
            data["replies"] = response_replies.json()
            data["permission_type"] = permission_type
            data["can_reply"] = PermissionService.can_reply_to_topic(permission_type, category_hidden)
            return templates.TemplateResponse("topic.html", data)

    @classmethod
    async def get_reply_form(cls, request: Request, topic_id: int):
        data = {"request": request, "title": "Reply to Topic - Forum API Frontend"}

        # Get authentication status
        token = Cookies.get_access_token_from_cookie(request)
        is_authenticated = token is not None
        data["is_authenticated"] = is_authenticated

        if not is_authenticated:
            return RedirectResponse(url="/auth/login")

        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        async with httpx.AsyncClient() as client:
            # Get topic details
            response_topic = await client.get(
                f"http://172.245.56.116:8000/topics/{topic_id}?token={token}", headers=headers)

            if response_topic.status_code == 404:
                return templates.TemplateResponse("404.html", data, status_code=404)

            if response_topic.status_code != 200:
                return templates.TemplateResponse("403.html", data, status_code=403)

            topic_data = response_topic.json()
            category_id = topic_data.get("category_id")

            # Check the user's permission for this category
            permission_type = await PermissionService.check_category_permission(request, category_id)

            # Get category details to check if it's hidden
            response_category = await client.get(
                f"http://172.245.56.116:8000/categories/{category_id}?token={token}", headers=headers)

            if response_category.status_code == 404:
                return templates.TemplateResponse("404.html", data, status_code=404)

            if response_category.status_code != 200:
                return templates.TemplateResponse("403.html", data, status_code=403)

            category_data = response_category.json()
            category_hidden = category_data.get("hidden", False)

            # Check if the user can reply to topics in this category
            if not PermissionService.can_reply_to_topic(permission_type, category_hidden):
                return templates.TemplateResponse("403.html", data, status_code=403)

            # Check if the user can view this category and its topics
            if not PermissionService.can_view_topics(permission_type, category_hidden):
                return templates.TemplateResponse("403.html", data, status_code=403)

            data["topic"] = topic_data
            data["permission_type"] = permission_type
            return templates.TemplateResponse("reply.html", data)

    @classmethod
    async def post_reply(cls, request: Request, topic_id: int):
        # Get authentication status
        token = Cookies.get_access_token_from_cookie(request)
        if not token:
            return RedirectResponse(url="/auth/login")

        # Get topic details to check category permissions
        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache"}
            if token:
                headers["Authorization"] = f"Bearer {token}"

            # Get topic details
            response_topic = await client.get(
                f"http://172.245.56.116:8000/topics/{topic_id}?token={token}", headers=headers)

            if response_topic.status_code == 404:
                return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

            if response_topic.status_code != 200:
                return templates.TemplateResponse("403.html", {"request": request}, status_code=403)

            topic_data = response_topic.json()
            category_id = topic_data.get("category_id")

            # Check the user's permission for this category
            permission_type = await PermissionService.check_category_permission(request, category_id)

            # Get category details to check if it's hidden
            response_category = await client.get(
                f"http://172.245.56.116:8000/categories/{category_id}?token={token}", headers=headers)

            if response_category.status_code == 404:
                return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

            if response_category.status_code != 200:
                return templates.TemplateResponse("403.html", {"request": request}, status_code=403)

            category_data = response_category.json()
            category_hidden = category_data.get("hidden", False)

            # Check if the user can reply to topics in this category
            if not PermissionService.can_reply_to_topic(permission_type, category_hidden):
                return templates.TemplateResponse("403.html", {"request": request}, status_code=403)

            # Check if the user can view this category and its topics
            if not PermissionService.can_view_topics(permission_type, category_hidden):
                return templates.TemplateResponse("403.html", {"request": request}, status_code=403)

            form_data = await request.form()
            content = form_data.get("content", "")

            # Post the reply using the correct API endpoint
            response = await client.post(
                f"http://172.245.56.116:8000/replies/add/{topic_id}?token={token}",
                json={"content": content},
                headers=headers
            )

            # Check if the reply was successfully posted
            if response.status_code != 200:
                data = {"request": request, "message": "Failed to post reply", "topic": topic_data}
                return templates.TemplateResponse("reply.html", data)

            # Redirect back to the topic page
            return RedirectResponse(url=f"/topics/{topic_id}", status_code=303)
