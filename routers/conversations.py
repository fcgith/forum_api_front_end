from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from services.conversations import ConversationsService

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def get_conversations(request: Request):
    return await ConversationsService.get_conversations(request)


@router.get("/new", response_class=HTMLResponse)
async def start_new_message_form(request: Request):
    return await ConversationsService.start_new_message_form(request)

@router.post("/new", response_class=HTMLResponse)
async def start_new_message_post(request: Request, username: str = Form(...)):
    return await ConversationsService.start_new_message_post(request, username)

@router.get("/{conversation_user_id}", response_class=HTMLResponse)
async def get_conversation_messages(request: Request, conversation_user_id: int):
    return await ConversationsService.get_conversation_messages(request, conversation_user_id)

@router.post("/{conversation_user_id}", response_class=HTMLResponse)
async def send_message(request: Request, conversation_user_id: int):
    return await ConversationsService.send_message(request, conversation_user_id)
