from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from services.conversations import ConversationsService

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def get_conversations(request: Request):
    return await ConversationsService.get_conversations(request)

@router.get("/{conversation_user_id}", response_class=HTMLResponse)
async def get_conversation_messages(request: Request, conversation_user_id: int):
    return await ConversationsService.get_conversation_messages(request, conversation_user_id)

@router.post("/{conversation_user_id}", response_class=HTMLResponse)
async def send_message(request: Request, conversation_user_id: int):
    return await ConversationsService.send_message(request, conversation_user_id)
