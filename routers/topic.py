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

@router.post("/{topic_id}/best-reply/{reply_id}", response_class=HTMLResponse)
async def mark_best_reply(request: Request, topic_id: int, reply_id: int):
    return await TopicService.mark_best_reply(request, reply_id, topic_id)

@router.post("/{topic_id}/vote/{reply_id}", response_class=HTMLResponse)
async def vote_reply(request: Request, topic_id: int, reply_id: int):
    form_data = await request.form()
    vote_type = int(form_data.get("vote_type", "0"))
    return await TopicService.vote_reply(request, reply_id, topic_id, vote_type)
