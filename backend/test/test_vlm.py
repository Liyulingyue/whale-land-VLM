## 图片识别需求

# 使用VLM的接口
# 输入一个图片 输出一个物品名称
import os
import base64
import yaml
from dotenv import load_dotenv
# from resize_img import resize_image,get_img_html
from zhipuai import ZhipuAI


def get_vlm_response(img_path, candidates, model_name="glm-4v-flash", max_tokens=2048):
    # img_path = r"asset\images\会员登记表.jpg"
    # img_path = r"asset\images\前台工作人员.jpg"
    # img_path= r"asset\images\烟头.jpg"
    with open(img_path, 'rb') as img_file:
        img_base = base64.b64encode(img_file.read()).decode('utf-8')

    prompt = """你是一个物品分类器。请根据图片内容，从以下候选列表中选择最匹配的一项作为分类结果。
            候选列表：{candidates}。请直接输出分类结果，不要包含任何其他描述或解释。"""
    # 使用f-string格式化prompt
    final_prompt = prompt.format(candidates=candidates)

    load_dotenv()
    your_api_key = os.getenv('ZHIPU_API_KEY')
    if not your_api_key:
        raise ValueError("请在.env项目文件中设置ZHIPU_API_KEY环境变量")
    
    client = ZhipuAI(api_key=your_api_key) # 填写您自己的APIKey
    response = client.chat.completions.create(
        model=model_name,  # 函数调用过程使用模型名称
        messages=[
        {
            "role": "user",
            "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": img_base
                }
            },
            {
                "type": "text",
                "text": final_prompt
            }
            ]
        }
        ]
    )
    return response.choices[0].message.content



# # 测试，输出结果
if __name__ == "__main__":
    img_path = r"asset\images\会员登记表.jpg"
    # img_path = r"asset\images\前台工作人员.jpg"
    candidates = ['人脸', '会员卡', '双节棍', '会员登记表']
    response = get_vlm_response(img_path, candidates)
    print(response)