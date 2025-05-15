from fastapi import FastAPI, Request, HTTPException
import uvicorn

from routers.main_service import router as main_router
from routers.auth import router as auth_router
from routers.user import router as user_router
from routers.category import router as categories_router
from routers.topic import router as topics_router
from routers.search import router as search_router
from routers.admin import router as admin_router
from routers.conversations import router as conversations_router

from services.jinja import templates

app = FastAPI()

app.include_router(main_router)
app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/user")
app.include_router(categories_router, prefix="/categories")
app.include_router(topics_router, prefix="/topics")
app.include_router(search_router, prefix="/search")
app.include_router(admin_router, prefix="/admin")
app.include_router(conversations_router, prefix="/conversations")

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse\
    (
        "404.html",
        {"request": request, "path": request.url.path},
        status_code=404
    )

@app.exception_handler(403)
async def custom_403_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse\
    (
        "403.html",
        {"request": request, "path": request.url.path},
        status_code=403
    )

@app.exception_handler(500)
async def custom_500_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse\
    (
        "500.html",
        {"request": request, "path": request.url.path},
        status_code=500
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
