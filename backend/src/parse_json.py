import json
import re


def markdown_to_json(markdown_str):
    # 移除Markdown语法中可能存在的标记，如代码块标记等
    markdown_str = markdown_str.strip()
    if markdown_str.startswith("```json"):
        markdown_str = markdown_str[7:-3].strip()
    elif markdown_str.startswith("```"):
        markdown_str = markdown_str[3:-3].strip()
    
    if markdown_str.endswith("```"):
        markdown_str = markdown_str[:-3].strip()

    # 将字符串转换为JSON字典
    json_dict = json.loads(markdown_str)

    return json_dict


def parse_json(json_str, forced_keywords=["character_response"]):
    try:
        return markdown_to_json(json_str)
    except:
        try:
            return forced_extract(json_str, forced_keywords)
        except:
            return {}


def forced_extract(input_str, keywords):
    result = {key: "" for key in keywords}

    for key in keywords:
        # 使用正则表达式来查找关键词-值对
        pattern = rf'"{key}":\s*"(.*?)"'
        match = re.search(pattern, input_str)
        if match:
            result[key] = match.group(1)
    
    return result
