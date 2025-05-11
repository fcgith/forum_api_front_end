from typing import Optional

from fastapi.responses import RedirectResponse
from fastapi import Request
from itsdangerous import URLSafeTimedSerializer
from fastapi.responses import Response

SECRET_KEY = "th34wiugbf43874g82fhgw85hfbwo3478f487fg8w"
serializer = URLSafeTimedSerializer(SECRET_KEY)

# Helper functions
class Cookies:
    @classmethod
    def set_token_cookie(cls, response: Response | RedirectResponse, access_token: str):
        """Set a signed access_token cookie in the response."""
        token_str = serializer.dumps({"access_token": access_token})
        response.set_cookie\
        (
            key="access_token",
            value=token_str,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=3600*8    # 8 hours
        )

    @classmethod
    def get_access_token_from_cookie(cls, request: Request) -> Optional[str]:
        """Get the access_token from the request cookies."""
        token_cookie = request.cookies.get("access_token")
        if not token_cookie:
            return None
        try:
            token_data = serializer.loads(token_cookie, max_age=3600*8)
            return token_data.get("access_token")
        except Exception:
            return None

    @classmethod
    def delete_token_cookie(cls):
        """Delete the access_token cookie from the response."""
        response = RedirectResponse(url="/", status_code=303)
        response.delete_cookie(key="access_token")
        return response