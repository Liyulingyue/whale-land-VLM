import os
from openai import OpenAI
from ..config.config import get_llm_config

class LLM:
    def __init__(self):
        llm_config = get_llm_config()
        
        # OpenAI兼容格式配置
        self.base_url = llm_config['base_url']
        self.api_key = llm_config['api_key']
        self.model_name = llm_config['model_name']

        if not self.api_key:
            raise ValueError("请在.env文件中设置LLM_API_KEY环境变量")
        
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

    def get_response(self, messages, max_tokens=-1, model_name=None):
        params = {
            "model": model_name or self.model_name,
            "messages": messages,
            "stream": False
        }

        if max_tokens > 0:
            params["max_tokens"] = max_tokens

        response = self.client.chat.completions.create(**params)
        return response.choices[0].message.content
    
llm_instance = LLM()

get_llm_response = llm_instance.get_response

if __name__ == '__main__':
    messages = [
        {"role": "user", "content": "你好"}
    ]
    try:
        content = get_llm_response(messages, max_tokens=200)
        print(content)
    except Exception as e:
        print(f"请求出错: {e}")
