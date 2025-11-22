from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import tempfile
from PIL import Image
from io import BytesIO
import base64
import time
import yaml

from ..src.GameMaster import GameMaster
from ..src.resize_img import resize_image

router = APIRouter()

# 全局游戏状态管理（后续可以改为 Redis 或数据库存储）
game_sessions = {}

# Session 时间戳管理
session_timestamps = {}

# 加载session配置
def load_session_config():
    from ..config.config import get_session_config
    session_config = get_session_config()
    return {"session_timeout_minutes": session_config['timeout_minutes']}

session_config = load_session_config()
SESSION_TIMEOUT_SECONDS = session_config.get("session_timeout_minutes", 20) * 60

def cleanup_expired_sessions():
    """清理超时的session"""
    current_time = time.time()
    expired_sessions = []
    
    for session_id, timestamp in session_timestamps.items():
        if current_time - timestamp > SESSION_TIMEOUT_SECONDS:
            expired_sessions.append(session_id)
    
    for session_id in expired_sessions:
        if session_id in game_sessions:
            del game_sessions[session_id]
        del session_timestamps[session_id]
        print(f"清理过期session: {session_id}")

def update_session_timestamp(session_id: str):
    """更新session的最后活动时间"""
    session_timestamps[session_id] = time.time()


class SessionCreate(BaseModel):
    session_id: str
    config_path: Optional[str] = "config/police.yaml"


class ChatMessage(BaseModel):
    session_id: str
    message: str


class ItemSubmit(BaseModel):
    session_id: str
    item_name: str


class ImageSubmit(BaseModel):
    session_id: str
    image_base64: str


@router.post("/session/create")
async def create_session(session_data: SessionCreate):
    """创建新的游戏会话"""
    try:
        # 清理过期session
        cleanup_expired_sessions()
        
        # 构建配置文件的完整路径
        config_path = os.path.join(os.path.dirname(__file__), "..", session_data.config_path)
        
        if not os.path.exists(config_path):
            raise HTTPException(status_code=404, detail=f"配置文件不存在: {session_data.config_path}")
        
        game_master = GameMaster(config_path)
        game_sessions[session_data.session_id] = game_master
        
        # 记录session创建时间
        update_session_timestamp(session_data.session_id)
        
        return {
            "session_id": session_data.session_id,
            "welcome_info": game_master.get_welcome_info(),
            "item_names": game_master.get_item_names(),
            "status": game_master.get_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建会话失败: {str(e)}")


@router.get("/session/{session_id}/status")
async def get_session_status(session_id: str):
    """获取会话状态"""
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    update_session_timestamp(session_id)
    game_master = game_sessions[session_id]
    return {
        "session_id": session_id,
        "status": game_master.get_status(),
        "item_names": game_master.get_item_names(),
        "welcome_info": game_master.get_welcome_info()
    }


@router.post("/session/{session_id}/reset")
async def reset_session(session_id: str, config_path: Optional[str] = None):
    """重置游戏会话"""
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    update_session_timestamp(session_id)
    
    try:
        if config_path is None:
            # 使用默认配置
            config_path = "config/police.yaml"
        
        full_config_path = os.path.join(os.path.dirname(__file__), "..", config_path)
        game_master = GameMaster(full_config_path)
        game_sessions[session_id] = game_master
        
        return {
            "session_id": session_id,
            "welcome_info": game_master.get_welcome_info(),
            "status": game_master.get_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重置会话失败: {str(e)}")


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


@router.post("/image/submit")
async def submit_image(image_data: ImageSubmit):
    """提交图片识别"""
    if image_data.session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="会话不存在，请先创建会话")
    
    update_session_timestamp(image_data.session_id)
    game_master = game_sessions[image_data.session_id]
    
    try:
        # 解码 base64 图片
        image_bytes = base64.b64decode(image_data.image_base64)
        image = Image.open(BytesIO(image_bytes))
        
        # 调整图片大小
        resized_img = resize_image(image, max_height=400)
        
        # 提交图片
        user_info, response = game_master.submit_image(resized_img)
        
        # 返回缩小后的图片用于显示
        display_img = resize_image(image, max_height=200)
        buffered = BytesIO()
        display_img.save(buffered, format="PNG")
        display_img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return {
            "user_info": user_info,
            "response": response,
            "status": game_master.get_status(),
            "display_image_base64": display_img_base64
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片提交失败: {str(e)}")


@router.post("/image/upload")
async def upload_image(session_id: str, file: UploadFile = File(...)):
    """上传图片文件"""
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="会话不存在，请先创建会话")
    
    update_session_timestamp(session_id)
    game_master = game_sessions[session_id]
    
    try:
        # 读取上传的文件
        contents = await file.read()
        image = Image.open(BytesIO(contents))
        
        # 调整图片大小用于识别
        resized_img_to_rec = resize_image(image, max_height=400)
        
        # 提交图片
        user_info, response = game_master.submit_image(resized_img_to_rec)
        
        # 返回缩小后的图片用于显示
        display_img = resize_image(image, max_height=200)
        buffered = BytesIO()
        display_img.save(buffered, format="PNG")
        display_img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return {
            "user_info": user_info,
            "response": response,
            "status": game_master.get_status(),
            "display_image_base64": display_img_base64
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片上传失败: {str(e)}")


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


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    del game_sessions[session_id]
    if session_id in session_timestamps:
        del session_timestamps[session_id]
    return {"message": "会话已删除", "session_id": session_id}
