from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from PIL import Image
from io import BytesIO
import base64

from ..src.resize_img import resize_image
from .session_routes import game_sessions, update_session_timestamp

router = APIRouter()


class ImageSubmit(BaseModel):
    session_id: str
    image_base64: str


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