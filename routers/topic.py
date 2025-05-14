from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from services.topic import TopicService

router = APIRouter()

@router.get("/{topic_id}", response_class=HTMLResponse)
async def get_topic(request: Request, topic_id: int, success: str = None):
    return await TopicService.get_topic(request, topic_id, success)

@router.get("/{topic_id}/reply", response_class=HTMLResponse)
async def get_reply_form(request: Request, topic_id: int):
    return await TopicService.get_reply_form(request, topic_id)

@router.post("/{topic_id}/reply", response_class=HTMLResponse)
async def post_reply(request: Request, topic_id: int):
    return await TopicService.post_reply(request, topic_id)
