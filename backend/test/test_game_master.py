
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.GameMaster import GameMaster
from src.resize_img import resize_image

yaml_path = "config/police.yaml"
gm = GameMaster(yaml_path)
print("GameMaster初始化成功！")
print("Prompt steps:", gm.prompt_steps)
print("Items:", gm.items)
# print(gm.name2img_path('双节棍'))
# print(gm.generate_item_response("手机"))
print(gm.use_record_images)
gm.init_image_master()
print(gm.use_record_images)

test_img_path = "local_data/base_image/一张人脸.jpg"
response = gm.submit_image(test_img_path)
print(response)

test_img_path = "local_data/base_image/知名开发者李鲁鲁_522WSFad.jpg"
resized_img = resize_image(test_img_path, max_height=200)
response = gm.submit_image(resized_img)
print(response)