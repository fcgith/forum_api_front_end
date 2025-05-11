from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import uvicorn

from routers.main import router as main_router
from routers.auth import router as auth_router
from routers.user import router as user_router

from services.jinja import templates

app = FastAPI()

app.include_router(main_router)
app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/user")

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
        status_code=404
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)