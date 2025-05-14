import httpx
from fastapi.responses import RedirectResponse

from services.auth import AuthService
from services.cookies import Cookies
from services.errors import not_authorized
from services.jinja import templates


class CategoryService:
    def __init__(self):
        pass

    @classmethod
    async def get_topic_form(cls, request, category):
        token = Cookies.get_access_token_from_cookie(request)
        data = await AuthService.get_user_data_from_cookie(request)

        if not data["is_authenticated"]:
            raise not_authorized

        async with httpx.AsyncClient() as client:
            headers = {"Cache-Control": "no-cache"}
            response_category = await client.get(f"http://172.245.56.116:8000/categories/{category}?token={token}", headers=headers)
            if response_category.status_code == 200:
                data["category"] = response_category.json()
                data["admin"] = True if data.get("admin") > 0 else False
                data["title"] = "Add Topic - Forum API Frontend"
                data["request"] = request

                return templates.TemplateResponse(
                    "addtopic.html",
                    data,
                    headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
                )
            else:
                raise not_authorized

    @classmethod
    async def get_category_by_id(cls, request, category):
        token = Cookies.get_access_token_from_cookie(request)
        data = await AuthService.get_user_data_from_cookie(request)

        if data["is_authenticated"]:
            async with httpx.AsyncClient() as client:
                headers = {"Cache-Control": "no-cache"}
                response_category = await client.get(f"http://172.245.56.116:8000/categories/{category}?token={token}",
                                                     headers=headers)
                response_topics = await client.get(
                    f"http://172.245.56.116:8000/categories/{category}/topics?token={token}", headers=headers)
                if response_category.status_code == 200 and response_topics.status_code == 200:
                    data["topics"] = response_topics.json()
                    data["category"] = response_category.json()
                    data["admin"] = True if data.get("admin") > 0 else False
                    data["title"] = "Category - Forum API Frontend"
                    data["request"] = request
                    return templates.TemplateResponse(
                        "category.html",
                        data,
                        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
                    )
                else:
                    if response_category.status_code == 403 or response_topics.status_code == 403:
                        raise not_authorized

        raise not_authorized

    @classmethod
    async def topic_form_post(cls, request, category_id: int):
        token = Cookies.get_access_token_from_cookie(request)
        data = await AuthService.get_user_data_from_cookie(request)

        if not data["is_authenticated"]:
            raise not_authorized

        form_data = await request.form()
        name = form_data.get("name")
        content = form_data.get("content")

        if not name or not content:
            # Return to the form with an error message if required fields are missing
            # Get the category details to maintain consistency with get_topic_form
            async with httpx.AsyncClient() as client:
                headers = {"Cache-Control": "no-cache"}
                response_category = await client.get(f"http://172.245.56.116:8000/categories/{category_id}?token={token}", headers=headers)
                if response_category.status_code == 200:
                    data["category"] = response_category.json()

            data["message"] = "Topic title and content are required."
            data["request"] = request
            data["title"] = "Add Topic - Forum API Frontend"
            return templates.TemplateResponse(
                "addtopic.html",
                data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )

        try:
            async with httpx.AsyncClient() as client:
                topic_data = {
                    "title": name,
                    "content": content,
                    "category_id": category_id
                }

                response = await client.post(
                    f"http://172.245.56.116:8000/topics/?token={token}",
                    json=topic_data,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 200 or response.status_code == 201:
                    # Redirect to the category page on success
                    return RedirectResponse(url=f"/categories/{category_id}", status_code=303)

                # Handle error response
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", error_data.get("detail", f"Error creating topic: {response.status_code}"))
                except ValueError:
                    error_message = f"Error creating topic: {response.status_code}"

                # Return to the form with the error message
                # Get the category details to maintain consistency with get_topic_form
                response_category = await client.get(f"http://172.245.56.116:8000/categories/{category_id}?token={token}", headers={"Cache-Control": "no-cache"})
                if response_category.status_code == 200:
                    data["category"] = response_category.json()

                data["message"] = error_message
                data["request"] = request
                data["title"] = "Add Topic - Forum API Frontend"
                return templates.TemplateResponse(
                    "addtopic.html",
                    data,
                    headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
                )

        except httpx.RequestError as e:
            # Handle connection errors
            # Get the category details to maintain consistency with get_topic_form
            try:
                async with httpx.AsyncClient() as client:
                    headers = {"Cache-Control": "no-cache"}
                    response_category = await client.get(f"http://172.245.56.116:8000/categories/{category_id}?token={token}", headers=headers)
                    if response_category.status_code == 200:
                        data["category"] = response_category.json()
            except:
                # If we can't get the category, we'll just continue without it
                pass

            data["message"] = f"Error connecting to API: {str(e)}"
            data["request"] = request
            data["title"] = "Add Topic - Forum API Frontend"
            return templates.TemplateResponse(
                "addtopic.html",
                data,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            )
