from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import base64
from io import BytesIO
from PIL import Image

from ..src.resize_img import resize_image
from .session_routes import game_sessions, update_session_timestamp

router = APIRouter()


class ItemSubmit(BaseModel):
    session_id: str
    item_name: str


@router.post("/item/submit")
async def submit_item(item_data: ItemSubmit):
    """提交物品"""
    if item_data.session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="会话不存在，请先创建会话")

    update_session_timestamp(item_data.session_id)
    game_master = game_sessions[item_data.session_id]

    try:
        user_info, response_info = game_master.submit_item(item_data.item_name)

        # 获取物品图片路径
        img_path = game_master.name2img_path(item_data.item_name)
        img_base64 = None

        if img_path and os.path.exists(img_path):
            try:
                resized_img = resize_image(img_path, max_height=200)
                buffered = BytesIO()
                resized_img.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            except Exception as e:
                print(f"图片处理失败: {e}")

        return {
            "user_info": user_info,
            "response_info": response_info,
            "status": game_master.get_status(),
            "image_base64": img_base64
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"物品提交失败: {str(e)}")


@router.get("/items/{session_id}")
async def get_items(session_id: str):
    """获取当前可用物品列表"""
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="会话不存在")

    update_session_timestamp(session_id)
    game_master = game_sessions[session_id]
    return {
        "items": game_master.get_item_names()
    }