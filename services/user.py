import httpx
from fastapi import Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from services.auth import AuthService
from services.cookies import Cookies
from services.errors import not_authorized, internal_error, not_found
from services.jinja import templates

class UserService:
    @classmethod
    async def get_user_profile(cls, request: Request):
        """
        Get the profile data for the currently logged-in user.

        Args:
            request: The FastAPI request object

        Returns:
            HTMLResponse: The rendered profile page
        """
        # Verify the user is logged in
        user_data = await AuthService.verify_logged_in(request)

        # Get the username from the user data
        username = user_data.get("username")
        if not username:
            raise not_authorized

        # Get the token from the cookie
        token = Cookies.get_access_token_from_cookie(request)
        if not token:
            raise not_authorized

        # Make the API call to get the user profile data
        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache", "Authorization": token}
            response = await client.get(
                f"http://172.245.56.116:8000/users/search/{username}",
                headers=headers
            )

            if response.status_code == 404:
                raise not_found

            if response.status_code != 200:
                raise not_authorized

            profile_data = response.json()

            # Prepare the data for the template
            template_data = user_data
            template_data = template_data | {
                "request": request,
                "title": f"Profile - {username}",
                "profile": profile_data,
                "is_authenticated": True,
                "admin": user_data.get("admin", False)
            }

            # Render the profile template
            return templates.TemplateResponse(
                "profile.html",
                template_data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )

    @classmethod
    async def get_user_by_id(cls, request: Request, user_id: int):
        """
        Get the profile data for a specific user by ID.

        Args:
            request: The FastAPI request object
            user_id: The ID of the user to get

        Returns:
            HTMLResponse: The rendered user profile page
        """
        # Get authentication status for the current user
        user_data = await AuthService.get_user_data_from_cookie(request)

        # Get the token from the cookie if the user is logged in
        token = Cookies.get_access_token_from_cookie(request)

        # Check if the user is logged in and viewing their own profile
        if user_data.get("is_authenticated") and "id" in user_data and user_data.get("id") == user_id:
            # Redirect to /user/me if the user is viewing their own profile
            return RedirectResponse(url="/user/me", status_code=303)

        # Make the API call to get the user profile data
        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache"}

            # Add token to the request if available
            api_url = f"http://172.245.56.116:8000/users/{user_id}"
            if token:
                api_url += f"?token={token}"
            else:
                raise not_authorized

            response = await client.get(api_url, headers=headers)

            if response.status_code == 404:
                raise not_found

            if response.status_code != 200:
                raise not_authorized

            profile_data = response.json()

            # Check if this is the user's own profile
            is_own_profile = user_data.get("is_authenticated") and "id" in user_data and user_data.get("id") == profile_data.get("id")

            # Prepare the data for the template
            template_data = user_data
            template_data = template_data | {
                "request": request,
                "title": f"User Profile - {profile_data.get('username', 'Unknown')}",
                "profile": profile_data,
                "is_authenticated": user_data.get("is_authenticated", False),
                "admin": user_data.get("admin", False),
                "is_own_profile": is_own_profile
            }

            # Render the user profile template
            return templates.TemplateResponse(
                "user_profile.html",
                template_data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )

    @classmethod
    async def get_avatar_change_page(cls, request: Request):
        """
        Display the avatar change page.

        Args:
            request: The FastAPI request object

        Returns:
            HTMLResponse: The rendered avatar change page
        """
        # Verify the user is logged in
        user_data = await AuthService.verify_logged_in(request)

        # Prepare the data for the template
        template_data = user_data
        template_data = template_data | {
            "request": request,
            "title": "Change Avatar",
            "is_authenticated": True,
            "admin": user_data.get("admin", False)
        }

        # Render the avatar change template
        return templates.TemplateResponse(
            "profile_avatar.html",
            template_data,
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )

    @classmethod
    async def update_avatar(cls, request: Request):
        """
        Process the avatar update form submission.

        Args:
            request: The FastAPI request object

        Returns:
            HTMLResponse: The rendered avatar change page with success/error message
        """
        # Verify the user is logged in
        user_data = await AuthService.verify_logged_in(request)

        # Get the token from the cookie
        token = Cookies.get_access_token_from_cookie(request)
        if not token:
            raise not_authorized

        # Get the form data
        form_data = await request.form()
        avatar_link = form_data.get("avatar_link")

        if not avatar_link:
            # Prepare the data for the template with error message
            template_data = user_data | {
                "request": request,
                "title": "Change Avatar",
                "is_authenticated": True,
                "admin": user_data.get("admin", False),
                "message": "Please provide an image URL",
                "success": False
            }

            # Render the avatar change template with error message
            return templates.TemplateResponse(
                "profile_avatar.html",
                template_data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )

        # Make the API call to update the avatar
        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(
                    f"http://172.245.56.116:8000/users/avatar/?link={avatar_link}",
                    headers={"Cache-Control": "no-cache", "Authorization": token}
                )

                # Prepare the template data based on the response
                template_data = user_data | {
                    "request": request,
                    "title": "Change Avatar",
                    "is_authenticated": True,
                    "admin": user_data.get("admin", False)
                }

                if response.status_code == 200:
                    template_data["message"] = "Avatar updated successfully!"
                    template_data["success"] = True
                else:
                    # Try to get error message from response
                    try:
                        error_data = response.json()
                        error_message = error_data.get("message", error_data.get("detail", f"Error updating avatar: {response.status_code}"))
                    except:
                        error_message = f"Error updating avatar: {response.status_code}"

                    template_data["message"] = error_message
                    template_data["success"] = False

                # Render the avatar change template with success/error message
                return templates.TemplateResponse(
                    "profile_avatar.html",
                    template_data,
                    headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
                )

            except httpx.RequestError as e:
                # Handle connection errors
                template_data = await AuthService.get_user_data_from_cookie(request) | {
                    "request": request,
                    "title": "Change Avatar",
                    "is_authenticated": True,
                    "admin": user_data.get("admin", False),
                    "message": f"Error connecting to API: {str(e)}",
                    "success": False
                }

                # Render the avatar change template with error message
                return templates.TemplateResponse(
                    "profile_avatar.html",
                    template_data,
                    headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
                )
