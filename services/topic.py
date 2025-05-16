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

            # Check if the current user is the topic creator
            # The user_id from the API response is the ID of the current user
            current_user_id = data.get("id")
            topic_creator_id = topic_data.get("user_id")
            data["is_topic_creator"] = current_user_id == topic_creator_id

            # Get the user's current vote for each reply
            replies = data["replies"]
            user_votes = {}

            for reply in replies:
                reply_id = reply.get("id")
                if reply_id:
                    response_vote = await client.get(
                        f"http://172.245.56.116:8000/replies/vote/{reply_id}?token={token}", headers=headers)

                    if response_vote.status_code == 200:
                        vote_data = response_vote.json()
                        user_votes[reply_id] = vote_data.get("vote_type", 0)
                    else:
                        user_votes[reply_id] = 0

            data["user_votes"] = user_votes


            return templates.TemplateResponse("topic.html", data)

    @classmethod
    async def get_reply_form(cls, request: Request, topic_id: int):
        data = {"request": request, "title": "Reply to Topic - Forum API Frontend"}

        # Get authentication status
        data = await AuthService.verify_logged_in(request)
        data["request"] = request
        data["title"] = "Reply to Topic - Forum API Frontend"

        if not data["is_authenticated"]:
            return RedirectResponse(url="/auth/login")

        # Get token for API requests
        token = Cookies.get_access_token_from_cookie(request)
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
        data = await AuthService.verify_logged_in(request)
        if not data["is_authenticated"]:
            return RedirectResponse(url="/auth/login")

        # Get token for API requests
        token = Cookies.get_access_token_from_cookie(request)

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

            # Convert newlines to <br /> tags
            content_with_br = content.replace('\n', '<br />')

            # Post the reply using the correct API endpoint
            response = await client.post(
                f"http://172.245.56.116:8000/replies/{topic_id}?token={token}",
                json={"content": content_with_br},
                headers=headers
            )

            if response.status_code == 403:
                data = {"request": request, "message": "The topic is locked.", "topic": topic_data}
                return templates.TemplateResponse("reply.html", data)

            # Check if the reply was successfully posted
            if response.status_code != 200:
                data = {"request": request, "message": "Failed to post reply", "topic": topic_data}
                return templates.TemplateResponse("reply.html", data)

            # Extract the reply_id from the API response
            response_data = response.json()
            reply_id = response_data.get("id")

            # Redirect back to the topic page with anchor to the new reply
            return RedirectResponse(url=f"/topics/{topic_id}#reply-{reply_id}", status_code=303)

    @classmethod
    async def mark_best_reply(cls, request: Request, reply_id: int, topic_id: int):
        """
        Mark a reply as the best reply for a topic.

        Args:
            request: The FastAPI request object
            reply_id: The ID of the reply to mark as best
            topic_id: The ID of the topic the reply belongs to

        Returns:
            RedirectResponse: Redirects back to the topic page
        """
        # Get authentication status
        data = await AuthService.verify_logged_in(request)
        if not data["is_authenticated"]:
            return RedirectResponse(url="/auth/login")

        # Get token for API requests
        token = Cookies.get_access_token_from_cookie(request)

        # Get topic details to check if the user is the topic creator
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

            # Get user data to check if the user is the topic creator
            user_data = await AuthService.get_user_data_from_cookie(request)
            current_user_id = user_data.get("id")
            topic_creator_id = topic_data.get("user_id")

            # Check if the user is the topic creator
            if current_user_id != topic_creator_id:
                return templates.TemplateResponse("403.html", {"request": request}, status_code=403)

            # Send PUT request to mark the reply as best
            response = await client.put(
                f"http://172.245.56.116:8000/replies/best/{topic_id}/{reply_id}?token={token}",
                headers=headers
            )

            # Check the status code from the PUT request
            if response.status_code == 403:
                return templates.TemplateResponse("403.html", {"request": request}, status_code=403)

            if response.status_code != 200:
                return templates.TemplateResponse("500.html", {"request": request}, status_code=500)

            # Redirect back to the topic page with anchor to the best reply
            return RedirectResponse(url=f"/topics/{topic_id}#reply-{reply_id}", status_code=303)

    @classmethod
    async def vote_reply(cls, request: Request, reply_id: int, topic_id: int, vote_type: int):
        """
        Vote on a reply (like, dislike, or remove vote).

        Args:
            request: The FastAPI request object
            reply_id: The ID of the reply to vote on
            topic_id: The ID of the topic the reply belongs to
            vote_type: The type of vote (-1 for dislike, 0 for removing vote, 1 for like)

        Returns:
            RedirectResponse: Redirects back to the topic page
        """
        # Get authentication status
        data = await AuthService.verify_logged_in(request)
        if not data["is_authenticated"]:
            return RedirectResponse(url="/auth/login")

        # Get token for API requests
        token = Cookies.get_access_token_from_cookie(request)

        # Send PUT request to vote on the reply
        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache"}
            if token:
                headers["Authorization"] = f"Bearer {token}"

            # Send PUT request to vote on the reply
            response = await client.put(
                f"http://172.245.56.116:8000/replies/vote/{reply_id}?token={token}",
                json={"vote_type": vote_type},
                headers=headers
            )

            # Check the status code from the PUT request
            if response.status_code == 403:
                return templates.TemplateResponse("403.html", {"request": request}, status_code=403)

            if response.status_code != 200:
                print(response.status_code)
                print(response.text)
                return templates.TemplateResponse("500.html", {"request": request}, status_code=500)

            # Redirect back to the topic page with anchor to the voted reply
            return RedirectResponse(url=f"/topics/{topic_id}#reply-{reply_id}", status_code=303)
