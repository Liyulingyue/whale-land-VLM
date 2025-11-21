import os
import base64
from dotenv import load_dotenv
from zhipuai import ZhipuAI
from io import BytesIO


def get_vlm_response_cot(resized_img, candidates, model_name="glm-4v-flash", max_tokens=-1):
    
    buffered = BytesIO()
    resized_img.save(buffered, format="JPEG")
    img_base = base64.b64encode(buffered.getvalue()).decode('utf-8')

    prompt = """请帮助我抽取图片中的主要物体，如果命中candidates中的物品，则按照candidates输出，否则，输出主要物品的名字
candidates: {candidates}

Let's think step by step and output in json format, 包括以下字段:
- caption 详细描述图像
- major_object 物品名称
- echo 重复字符串: 我将检查candidates中的物品，如果major_object有同义词在candidates中，则修正为candidate对应的名字，不然则保留major_object
- fixed_object_name: 检查candidates后修正（如果命中）的名词，如果不命中则重复输出major_object
"""
    final_prompt = prompt.format(candidates=candidates)

    load_dotenv()
    your_api_key = os.getenv('ZHIPU_API_KEY')
    if not your_api_key:
        raise ValueError("请在.env项目文件中设置ZHIPU_API_KEY环境变量")
    
    client = ZhipuAI(api_key=your_api_key)

    response = client.chat.completions.create(
        model=model_name,
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


def get_vlm_response(img_path, candidates, model_name="glm-4v-flash", max_tokens=2048):
    with open(img_path, 'rb') as img_file:
        img_base = base64.b64encode(img_file.read()).decode('utf-8')

    prompt = """你是一个物品分类器。请根据图片内容，从以下候选列表中选择最匹配的一项作为分类结果。
            候选列表：{candidates}。请直接输出分类结果，不要包含任何其他描述或解释。"""
    final_prompt = prompt.format(candidates=candidates)

    load_dotenv()
    your_api_key = os.getenv('ZHIPU_API_KEY')
    if not your_api_key:
        raise ValueError("请在.env项目文件中设置ZHIPU_API_KEY环境变量")
    
    client = ZhipuAI(api_key=your_api_key)
    response = client.chat.completions.create(
        model=model_name,
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
