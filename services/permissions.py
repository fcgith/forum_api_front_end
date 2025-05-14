import httpx
from services.cookies import Cookies

class PermissionService:
    # Permission types
    NO_ACCESS = "no_access"
    NORMAL_ACCESS = "normal_access"
    READ_ONLY_ACCESS = "read_only_access"
    WRITE_ACCESS = "write_access"

    @classmethod
    async def check_category_permission(cls, request, category_id):
        """
        Check the user's permission for a specific category.

        Args:
            request: The FastAPI request object
            category_id: The ID of the category to check permissions for

        Returns:
            str: The permission type (no_access, normal_access, read_only_access, write_access)
        """
        token = Cookies.get_access_token_from_cookie(request)
        if not token:
            return cls.NO_ACCESS

        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache"}
            response = await client.get(
                f"http://172.245.56.116:8000/categories/{category_id}/check-permission?token={token}",
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("access_type", cls.NO_ACCESS)

            # If there's an error with the API call, default to no access
            return cls.NO_ACCESS

    @classmethod
    def can_view_category(cls, permission_type, category_hidden=False):
        """
        Check if the user can view the category based on their permission type.

        Args:
            permission_type: The user's permission type
            category_hidden: Whether the category is hidden

        Returns:
            bool: True if the user can view the category, False otherwise
        """
        # Use case-insensitive comparison for consistency
        if permission_type.lower() == cls.NO_ACCESS.lower():
            return False

        # Fix for normal_access users not being able to view categories
        # Use string comparison instead of direct equality check
        if permission_type.lower() == cls.NORMAL_ACCESS.lower() and category_hidden:
            return False

        # Explicitly handle read_only_access permission type
        if permission_type.lower() == cls.READ_ONLY_ACCESS.lower():
            return True

        return True

    @classmethod
    def can_view_topics(cls, permission_type, category_hidden=False):
        """
        Check if the user can view topics in the category based on their permission type.

        Args:
            permission_type: The user's permission type
            category_hidden: Whether the category is hidden

        Returns:
            bool: True if the user can view topics, False otherwise
        """
        return cls.can_view_category(permission_type, category_hidden)

    @classmethod
    def can_add_topic(cls, permission_type, category_hidden=False):
        """
        Check if the user can add a topic to the category based on their permission type.

        Args:
            permission_type: The user's permission type
            category_hidden: Whether the category is hidden

        Returns:
            bool: True if the user can add a topic, False otherwise
        """
        # Use case-insensitive comparison for consistency
        if permission_type.lower() == cls.WRITE_ACCESS.lower():
            return True

        # Normal access users can only add topics to non-hidden categories
        if permission_type.lower() == cls.NORMAL_ACCESS.lower():
            return not category_hidden

        return False

    @classmethod
    def can_reply_to_topic(cls, permission_type, category_hidden=False):
        """
        Check if the user can reply to a topic based on their permission type.

        Args:
            permission_type: The user's permission type
            category_hidden: Whether the category is hidden

        Returns:
            bool: True if the user can reply to a topic, False otherwise
        """
        # Use case-insensitive comparison for consistency
        if permission_type.lower() == cls.WRITE_ACCESS.lower():
            return True

        # Normal access users can only reply to topics in non-hidden categories
        if permission_type.lower() == cls.NORMAL_ACCESS.lower():
            return not category_hidden

        return False
