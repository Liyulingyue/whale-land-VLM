import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.resize_img import resize_image, get_img_html

if __name__ == "__main__":
    image_indices = [1, 2, 3]
    for i in image_indices:
        img_path = "asset/images/鲸娱秘境{}.jpg".format(i)
        resized_img = resize_image(img_path, max_height=300)
        img_html = get_img_html(resized_img).replace('200px', '300px')
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demo_info.md"), "a", encoding="utf-8") as f:
            f.write(img_html + "\n")

