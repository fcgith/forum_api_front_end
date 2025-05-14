from fastapi import Request

from services.auth import AuthService
from services.errors import not_authorized


class SearchService:
    @classmethod
    async def get_main_page(cls, request: Request):
        user_data = await AuthService.get_user_data_from_cookie(request)
        if not user_data["is_authenticated"]:
            raise not_authorized

        token = user_data["access_token"]

        # the service will connect to the api and acquire a dict of two items:
        # - page count
        # - a list of all topics to display

    @classmethod
    async def search(cls, request: Request, query: str, page: int, sort: str):
        pass