"""
API路由聚合文件
将所有路由模块整合到一起
"""

from fastapi import APIRouter

# 导入各个路由模块
from .session_routes import router as session_router
from .chat_routes import router as chat_router
from .item_routes import router as item_router
from .image_routes import router as image_router

# 创建主路由器
router = APIRouter()

# 包含所有子路由
router.include_router(session_router)
router.include_router(chat_router)
router.include_router(item_router)
router.include_router(image_router)
