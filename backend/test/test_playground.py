from src.GameMaster import GameMaster
from src.resize_img import resize_image


yaml_path = "config/police.yaml"
gm = GameMaster(yaml_path)
print("GameMaster初始化成功！")
print("Prompt steps:", gm.prompt_steps)
print("Items:", gm.items)
print(gm.name2img_path('双节棍'))
print("===Response to 手机===")
print(gm.generate_item_response("手机"))

print("-----")

# image_name = "asset/images/会员卡.jpg"
# image_name = "asset/images/会员登记表.jpg"
image_name = "asset/images/前台工作人员.jpg"



# 参考 resized_img 读取image_name, 并且resize到max_height = 200
resized_img = resize_image(image_name, max_height=200)

# 只上传图片的相对路径
response = gm.extract_object_from_image(resized_img)
print("用户上传的图片识别为:")
print(response)
