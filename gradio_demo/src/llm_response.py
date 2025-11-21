import os
from dotenv import load_dotenv
from openai import OpenAI

class LLM:
    def __init__(self):
        load_dotenv()
        llm_backend = os.getenv('LLM_BACKEND', 'openai')
        if llm_backend == 'openai':
            self.base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
            self.api_key = os.getenv('OPENAI_API_KEY')
        elif llm_backend == 'siliconflow':
            self.base_url = os.getenv('SILICONFLOW_BASE_URL', 'https://api.siliconflow.cn/v1')
            self.api_key = os.getenv('SILICONFLOW_API_KEY')
        elif llm_backend == 'zhipu':
            self.base_url = os.getenv('ZHIPU_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4')
            self.api_key = os.getenv('ZHIPU_API_KEY')
        elif llm_backend == 'openvino':
            self.base_url = os.getenv('OPENVINO_BASE_URL', 'http://localhost:8000/v1')
            self.api_key = os.getenv('OPENVINO_API_KEY')
            print("Using Intel© OpenVINO™ backend")
        else:
            raise ValueError(f"Unsupported LLM backend: {llm_backend}")

        if not self.api_key:
            raise ValueError(f"请在.env项目文件中设置{llm_backend.upper()}_API_KEY环境变量")
        
        self.model_name = os.getenv('MODEL_NAME', 'gpt-4.1-mini')

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
