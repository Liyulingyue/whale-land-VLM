from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .session_routes import game_sessions, update_session_timestamp

router = APIRouter()


class ChatMessage(BaseModel):
    session_id: str
    message: str


@router.post("/chat")
async def chat(chat_data: ChatMessage):
    """处理聊天消息"""
    if chat_data.session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="会话不存在，请先创建会话")

    update_session_timestamp(chat_data.session_id)
    game_master = game_sessions[chat_data.session_id]

    try:
        user_input, bot_response = game_master.submit_chat(chat_data.message)
        return {
            "user_input": user_input,
            "bot_response": bot_response,
            "status": game_master.get_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"聊天处理失败: {str(e)}")