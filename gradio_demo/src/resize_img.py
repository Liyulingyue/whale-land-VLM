from PIL import Image
import base64
from io import BytesIO


def resize_image(img_path, max_height=200):
    img = Image.open(img_path)
    w, h = img.size
    new_h = min(h, max_height)
    new_w = int(w * (new_h / h))
    img = img.resize((new_w, new_h))
    return img
    
def get_img_html(resized_img):
    buffered = BytesIO()
    resized_img.save(buffered, format="PNG")  # 也可以改成 JPEG
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    # return img_base64
    max_height = 200
    # 用 HTML 或 Markdown 插入图片（固定高度）
    img_html = f'<img src="data:image/png;base64,{img_base64}" style="max-height:{max_height}px; width:auto;">'
    return img_html