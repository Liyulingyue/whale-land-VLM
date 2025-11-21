
import json


def markdown_to_json(markdown_str):
    # 移除Markdown语法中可能存在的标记，如代码块标记等
    markdown_str = markdown_str.strip()
    if markdown_str.startswith("```json"):
        markdown_str = markdown_str[7:-3].strip()
    elif markdown_str.startswith("```"):
        markdown_str = markdown_str[3:-3].strip()
    
    if markdown_str.endswith("```"):
        markdown_str = markdown_str[:-3].strip()

    # print(markdown_str)

    # 将字符串转换为JSON字典
    json_dict = json.loads(markdown_str)

    return json_dict


def parse_json(json_str, forced_keywords= ["character_response"]):
    try:
        return markdown_to_json(json_str)
    except:
        try:
            return forced_extract(json_str, forced_keywords)
        except:
            return {}


import re

def forced_extract(input_str, keywords):
    result = {key: "" for key in keywords}

    for key in keywords:
        # 使用正则表达式来查找关键词-值对
        pattern = f'"{key}":\s*"(.*?)"'
        match = re.search(pattern, input_str)
        if match:
            result[key] = match.group(1)
    
    return result


if __name__ == "__main__":
    input_str = """```json
{
  "item_name": "手机",
  "analysis": "在剧情中，手机作为一个可能的线索，可能会含有凶手的通讯记录或者与受害者最后的联系信息。队长李伟会指示队员们检查手机，以寻找可能的线索，如通话记录、短信、社
交媒体应用等。",
  "echo": "我认为在剧情设定的人物眼里，看到物品 手机时，会说",
  "character_response": "队长李伟可能会说：'这手机可能是死者最后的通讯工具，检查一下有没有未接电话或者最近的通话记录，看看能否找到凶手的线索。'"
}
```"""
    print(parse_json(input_str))

#     center_str = """{
#   "item_name": "手机",
#   "analysis": "在剧情中，手机作为一个可能的线索，可能会含有凶手的通讯记录或者与受害者最后的联系信息。队长李伟会指示队员们检查手机，以寻找可能的线索，如通话记录、短信、社
# 交媒体应用等。",
#   "echo": "我认为在剧情设定的人物眼里，看到物品 手机时，会说",
#   "character_response": "队长李伟可能会说：'这手机可能是死者最后的通讯工具，检查一下有没有未接电话或者最近的通话记录，看看能否找到凶手的线索。'"
# }"""
#     json_dict = json.loads(center_str)