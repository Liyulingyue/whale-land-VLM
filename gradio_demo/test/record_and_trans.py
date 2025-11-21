'''
我需要实现一个简单的opencv循环

当按下空格键的时候，会在local_data/new_image 目录下

以 record_{8位随机大小写字母或者数字}.jpg 命名

- 整体程序开机前会检查cam_id为1的摄像头，如果摄像头读取不到或者边长小于100，使用cam_id = 0的摄像头
- 整体程序开机前，将local_data下所有不是以record_ 开头的.jpg文件，移动到 local_data/base_image
- 空格按键有0.3秒的cooldown 防止一次按键记录下非常多的照片
'''

import sys
import os

# 在这里修正帮助我找到ImageMaster
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import cv2
import os
import random
import string
import time
import shutil
from pathlib import Path
from src.ImageMaster import ImageMaster
from PIL import Image

cam_id_seqs = [0,1]

# 设置目录路径
PROJECT_ROOT = Path(__file__).parent.parent
LOCAL_DATA = PROJECT_ROOT / 'local_data'
NEW_IMAGE_DIR = LOCAL_DATA / 'new_image'
BASE_IMAGE_DIR = LOCAL_DATA / 'base_image'
CONFIG_PATH = PROJECT_ROOT / 'config' / 'image_master.yaml'

image_master = ImageMaster()
image_master.set_from_config(CONFIG_PATH)
# 初始化模型
print("正在初始化模型...")
image_master.init_model()
image_master.load_database()

'''
TODO: 回车按下时
 使用 results = image_master.extract_item_from_image(frame)
 来获得识别结果
for result in results:
                print(f"  匹配: {result['name']} (相似度: {result['similarity']:.4f})")
来打印结果
'''

# 创建必要的目录
for dir_path in [LOCAL_DATA, NEW_IMAGE_DIR, BASE_IMAGE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# 移动非record_开头的jpg文件到base_image目录
if NEW_IMAGE_DIR.exists():
    for file in NEW_IMAGE_DIR.glob('*.jpg'):
        if not file.name.startswith('record_'):
            dest_path = BASE_IMAGE_DIR / file.name
            # 如果目标文件已存在，添加时间戳避免覆盖
            if dest_path.exists():
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                dest_path = dest_path.with_name(f'{dest_path.stem}_{timestamp}{dest_path.suffix}')
            shutil.move(str(file), str(dest_path))

def select_camera():
    """选择合适的摄像头"""
    for cam_id in cam_id_seqs:
        cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)  # 使用CAP_DSHOW加速Windows摄像头访问
        if cap.isOpened():
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            if min(width, height) >= 100:
                return cap
            else:
                cap.release()
    raise Exception("未找到可用摄像头")

def generate_random_filename(length=8):
    """生成8位随机文件名"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

def main():
    # 选择摄像头
    try:
        cap = select_camera()
    except Exception as e:
        print(f"摄像头初始化失败: {e}")
        return

    last_capture_time = 0
    capture_cooldown = 0.3  # 0.3秒冷却时间

    print("程序已启动，按空格键拍照，按ESC键退出")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法获取图像帧")
            break

        frame = cv2.flip(frame, 1)
        # 显示图像
        cv2.imshow('Camera', frame)

        # 处理按键
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC键退出
            break
        elif key == ord(' '):  # 空格键拍照
            current_time = time.time()
            if current_time - last_capture_time >= capture_cooldown:
                # 生成文件名
                random_str = generate_random_filename()
                filename = f'record_{random_str}.jpg'
                save_path = NEW_IMAGE_DIR / filename
                
                # 保存图像
                if cv2.imwrite(str(save_path), frame):
                    print(f"照片已保存: {save_path}")
                    last_capture_time = current_time
                else:
                    print("保存照片失败")
        elif key == 13:  # 回车键识别
            print("正在识别图像...")
            PIL_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            results = image_master.extract_item_from_image(PIL_frame)
            if results:
                print(f"识别到 {len(results)} 个对象:")
                for result in results:
                    print(f"  匹配: {result['name']} (相似度: {result['similarity']:.4f})")
            else:
                print("未识别到任何对象")

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

