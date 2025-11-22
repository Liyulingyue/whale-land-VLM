from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import time

from ..src.GameMaster import GameMaster
from ..config.config import get_session_config

router = APIRouter()

# 全局游戏状态管理（后续可以改为 Redis 或数据库存储）
game_sessions = {}

# Session 时间戳管理
session_timestamps = {}

# 加载session配置
def load_session_config():
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


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="会话不存在")

    del game_sessions[session_id]
    if session_id in session_timestamps:
        del session_timestamps[session_id]
    return {"message": "会话已删除", "session_id": session_id}