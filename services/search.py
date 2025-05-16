from fastapi import Request
import httpx

from services.auth import AuthService
from services.cookies import Cookies
from services.errors import not_authorized
from services.jinja import templates


class SearchService:
    @classmethod
    async def get_main_page(cls, request: Request):
        user_data = await AuthService.get_user_data_from_cookie(request)
        if not user_data["is_authenticated"]:
            raise not_authorized

        token = Cookies.get_access_token_from_cookie(request)

        # Connect to the API to get search results with only the token
        # Use page=0 for the first page because API uses 0-based indexing
        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache"}
            response = await client.get(
                f"http://172.245.56.116:8000/topics/?token={token}&page=0",
                headers=headers
            )

            if response.status_code != 200:
                raise not_authorized

            # Parse the response
            response_data = response.json()
            topics = response_data.get("topics", [])
            # API returns the total number of pages
            pages = response_data.get("pages", 1)

            # Prepare data for the template
            data = {
                "request": request,
                "title": "Search - Forum API Frontend",
                "topics": topics,
                "search": "",
                "sort": "desc",
                "current_page": 1,
                "pages": pages,
                "is_authenticated": user_data["is_authenticated"],
                "admin": True if user_data.get("admin") > 0 else False
            }

            return templates.TemplateResponse(
                "search.html",
                data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )

    @classmethod
    async def search(cls, request: Request, search: str, page: int, sort: str):
        user_data = await AuthService.get_user_data_from_cookie(request)
        if not user_data["is_authenticated"]:
            raise not_authorized

        token = Cookies.get_access_token_from_cookie(request)

        # Connect to the API to get search results
        # Subtract 1 from page number because API uses 0-based indexing
        api_page = page - 1
        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache"}
            response = await client.get(
                f"http://172.245.56.116:8000/topics/?token={token}&search={search}&page={api_page}&sort={sort}",
                headers=headers
            )

            if response.status_code != 200:
                raise not_authorized

            # Parse the response
            response_data = response.json()
            topics = response_data.get("topics", [])
            # API returns the total number of pages
            pages = response_data.get("pages")
            if pages == 0:
                pages = 1
            else:
                pages += 1
            # Prepare data for the template
            data = user_data | {
                "request": request,
                "title": "Search Results - Forum API Frontend",
                "topics": topics,
                "search": search,
                "sort": sort,
                "current_page": page,
                "pages": pages
            }

            return templates.TemplateResponse(
                "search.html",
                data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )
