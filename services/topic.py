import httpx
from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse

from services.auth import AuthService
from services.errors import not_authorized, internal_error
from services.jinja import templates
from services.cookies import Cookies

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

            # Get replies for the topic
            response_replies = await client.get(
                f"http://172.245.56.116:8000/topics/{topic_id}/replies?token={token}", headers=headers)

            if response_topic.status_code == 200 and response_replies.status_code == 200:
                data["topic"] = response_topic.json()
                data["replies"] = response_replies.json()
                return templates.TemplateResponse("topic.html", data)

            if response_topic.status_code == 403 or response_replies.status_code == 403:
                raise not_authorized

            raise internal_error

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

            if response_topic.status_code == 200:
                data["topic"] = response_topic.json()
                return templates.TemplateResponse("reply.html", data)

            if response_topic.status_code == 403:
                return templates.TemplateResponse("403.html", data, status_code=403)

            return templates.TemplateResponse("404.html", data, status_code=404)

    @classmethod
    async def post_reply(cls, request: Request, topic_id: int):
        # Get authentication status
        token = Cookies.get_access_token_from_cookie(request)
        if not token:
            return RedirectResponse(url="/auth/login")

        form_data = await request.form()
        content = form_data.get("content", "")

        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            # Post the reply
            response = await client.post(
                f"http://172.245.56.116:8000/topics/{topic_id}/replies",
                json={"content": content},
                headers=headers
            )

            # Redirect back to the topic page
            return RedirectResponse(url=f"/topics/{topic_id}", status_code=303)
