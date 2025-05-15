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
                        f"http://172.245.56.116:8000/conversations/last-message/?user_id={user['id']}&token={token}",
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
    async def get_conversation_messages(cls, request, conversation_user_id):
        token = Cookies.get_access_token_from_cookie(request)
        data = await AuthService.get_user_data_from_cookie(request)

        if not data["is_authenticated"]:
            raise not_authorized

        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache"}

            # Get conversation partner details
            user_response = await client.get(
                f"http://172.245.56.116:8000/users/{conversation_user_id}?token={token}",
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

            # Get authenticated user details
            auth_user_response = await client.get(
                f"http://172.245.56.116:8000/users/{data.get('id')}?token={token}",
                headers=headers
            )

            if auth_user_response.status_code == 200:
                auth_user = auth_user_response.json()
            else:
                auth_user = {"username": data.get("username"), "avatar": None}

            data["conversation_user"] = conversation_user
            data["messages"] = messages
            data["user_id"] = data.get("id")  # Pass the authenticated user's ID to the template
            data["auth_user"] = auth_user  # Pass the authenticated user's data to the template
            data["admin"] = True if data.get("admin") > 0 else False
            data["title"] = f"Conversation with {conversation_user['username']} - Forum API Frontend"
            data["request"] = request

            return templates.TemplateResponse(
                "conversation_messages.html",
                data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )
