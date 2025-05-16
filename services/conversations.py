import httpx
from fastapi.responses import RedirectResponse

from services.auth import AuthService
from services.cookies import Cookies
from services.errors import not_authorized, not_found
from services.jinja import templates


class ConversationsService:
    def __init__(self):
        pass

    @classmethod
    async def get_conversations(cls, request):
        token = Cookies.get_access_token_from_cookie(request)
        data = await AuthService.get_user_data_from_cookie(request)

        if not data["is_authenticated"]:
            raise not_authorized

        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache"}
            response = await client.get(f"http://172.245.56.116:8000/conversations/?token={token}", headers=headers)

            if response.status_code == 404:
                raise not_found

            if response.status_code != 200:
                raise not_authorized

            conversations = response.json()

            # Fetch last message for each conversation
            for user in conversations:
                try:
                    last_message_response = await client.get(
                        f"http://172.245.56.116:8000/conversations/last-message/{user['id']}?token={token}",
                        headers=headers
                    )

                    if last_message_response.status_code == 200:
                        last_message = last_message_response.json()
                        # Add the last message to the user object
                        user['last_message'] = last_message
                        # Truncate the content if it's too long
                        if 'content' in last_message and last_message['content']:
                            user['last_message_content'] = last_message['content'][:50] + ('...' if len(last_message['content']) > 50 else '')
                        else:
                            user['last_message_content'] = "No messages yet"
                    else:
                        user['last_message'] = None
                        user['last_message_content'] = "No messages yet"
                except Exception as e:
                    # Handle any errors that might occur during the API call
                    user['last_message'] = None
                    user['last_message_content'] = "Error fetching message"

            data["conversations"] = conversations
            data["admin"] = True if data.get("admin") > 0 else False
            data["title"] = "Conversations - Forum API Frontend"
            data["request"] = request

            return templates.TemplateResponse(
                "conversations.html",
                data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )

    @classmethod
    async def get_conversation_messages(cls, request, conversation_user_id, error_message=None):
        token = Cookies.get_access_token_from_cookie(request)
        data = await AuthService.get_user_data_from_cookie(request)

        if not data["is_authenticated"]:
            return RedirectResponse(url="/auth/login", status_code=303)

        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache", "Authorization": token}

            user_response = await client.get(
                f"http://172.245.56.116:8000/users/{conversation_user_id}",
                headers=headers
            )

            if user_response.status_code == 404:
                raise not_found

            if user_response.status_code != 200:
                raise not_authorized

            conversation_user = user_response.json()

            # Fetch messages between users
            try:
                messages_response = await client.get(
                    f"http://172.245.56.116:8000/conversations/msg/{conversation_user_id}?token={token}",
                    headers=headers
                )

                if messages_response.status_code == 200:
                    messages = messages_response.json()
                else:
                    messages = []
            except Exception as e:
                # Handle any errors that might occur during the API call
                messages = []

            data["conversation_user"] = conversation_user
            data["messages"] = messages
            data["user_id"] = data.get("id")  # Pass the authenticated user's ID to the template
            data["admin"] = True if data.get("admin") > 0 else False
            data["title"] = f"Conversation with {conversation_user['username']} - Forum API Frontend"
            data["request"] = request

            # Add error message if provided
            if error_message:
                data["error_message"] = error_message

            return templates.TemplateResponse(
                "conversation_messages.html",
                data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )

    @classmethod
    async def send_message(cls, request, conversation_user_id):
        token = Cookies.get_access_token_from_cookie(request)
        data = await AuthService.get_user_data_from_cookie(request)

        if not data["is_authenticated"]:
            raise not_authorized

        # Get form data
        form_data = await request.form()
        message_content = form_data.get("message")

        if not message_content:
            # Return to the conversation page with an error message
            return await cls.get_conversation_messages(request, conversation_user_id, error_message="Message cannot be empty")

        # Prepare the request body
        message_data = {
            "content": message_content,
            "receiver_id": conversation_user_id
        }

        # Send the message to the API
        async with httpx.AsyncClient() as client:
            headers = {"Content-Type": "application/json", "Cache-Control": "no-cache"}
            try:
                response = await client.post(
                    f"http://172.245.56.116:8000/conversations/messages/?token={token}",
                    json=message_data,
                    headers=headers
                )

                # Check if the message was sent successfully
                if response.status_code == 200 or response.status_code == 201:
                    # Redirect back to the conversation page
                    return RedirectResponse(url=f"/conversations/{conversation_user_id}", status_code=303)
                else:
                    # Try to get error message from response
                    try:
                        error_data = response.json()
                        error_message = error_data.get("message", error_data.get("detail", f"Error sending message: {response.status_code}"))
                    except:
                        error_message = f"Error sending message: {response.status_code}"

                    # Return to the conversation page with the error message
                    return await cls.get_conversation_messages(request, conversation_user_id, error_message=error_message)

            except httpx.RequestError as e:
                # Handle connection errors
                error_message = f"Error connecting to API: {str(e)}"
                return await cls.get_conversation_messages(request, conversation_user_id, error_message=error_message)

    @classmethod
    async def start_new_message_form(cls, request, message=None):
        data = await AuthService.get_user_data_from_cookie(request)
        if not data["is_authenticated"]:
            return RedirectResponse(url="/auth/login")

        data["request"] = request
        data["title"] = "New Conversation - Forum API Frontend"
        data["message"] = message

        return templates.TemplateResponse(
            "conversations/new_conversation_form.html",
            data,
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )

    @classmethod
    async def start_new_message_post(cls, request, username):
        token = Cookies.get_access_token_from_cookie(request)
        data = await AuthService.get_user_data_from_cookie(request)
        if not data["is_authenticated"]:
            return RedirectResponse(url="/auth/login")

        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://172.245.56.116:8000/users/search/{username}",
                                        headers={"Cache-Control": "no-cache", "Authorization": token})
            if response.status_code == 200:
                user_data = response.json()
                return RedirectResponse(url=f"/conversations/{user_data.get("id")}", status_code=303)
            message = f"Oops! {response.json().get('detail', 'Unknown error')}"
            return await cls.start_new_message_form(request, message=message)
