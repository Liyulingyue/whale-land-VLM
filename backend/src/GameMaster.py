from .llm_response import get_llm_response
from .parse_json import parse_json
# from .recognize_from_image_glm import get_vlm_response
from .recognize_from_image_glm import get_vlm_response_cot


class GameMaster:

    def __init__(self, yaml_file_path = None):
        self.status = set()
        self.history = []

        self.items = []
        self.prompt_steps = []

        self.history_messages = [] # 以文字形式存储的过往历史对话
        
        self.item_expand_name2name = {}

        self.item2cache_text = {}

        self.current_step = {
            # default welcome info
            "welcome_info": "欢迎来到游戏，快来和我一起探索吧",
            "prompt": "",
            "conds": []
        }
        
        if yaml_file_path is not None:
            self.prompt_steps, self.items, self.use_record_images = self.load_yaml(yaml_file_path)
            if len(self.prompt_steps) > 0:
                self.current_step = self.prompt_steps[0]
                self.current_index = 0
            else:
                print("没有成功从yaml载入关卡 使用了默认的example NPC")
            self.item2text = self.load_default_item_text_map( self.items )
            welcome_message = {
                "role": "assistant",
                "content": self.current_step["welcome_info"]
            }
            self.history_messages.append(welcome_message)
        else:
            self.item2text = self.load_default_item_text_map()

    def init_image_master(self, config_path = None):
        from .ImageMaster import ImageMaster
        print("正在初始化image_master")
        self.image_master = ImageMaster()
        if config_path is None:
            config_path = "config/image_master.yaml"
        self.image_master.set_from_config(config_path) 
        self.image_master.init_model()
        self.image_master.load_database()
        self.use_record_images = True


    def load_yaml(self, yaml_file_path):
        '''
        从yaml中读取prompt_steps和items并返回
        '''
        import yaml
        with open(yaml_file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        prompt_steps = data['prompt_steps']
        items = []
        for item in data['items']:
            items.append({
                'name': item['name'],
                'text': item['text'],
                'img_path' : item['img_path']
            })

        if 'record_image_threshold' in data:
            self.record_image_threshold = data['record_image_threshold']
        else:
            self.record_image_threshold = 0.89

        if 'use_record_images' in data:
            use_record_images = data['use_record_images']
        else:
            use_record_images = False

        if use_record_images:
            self.init_image_master()
        
        return prompt_steps, items, use_record_images

    def name2img_path(self, name):
        for item in self.items:
            if item['name'] == name:
                return item['img_path']
        return None
        

    def load_default_item_text_map(self, items = None):
        
        item2text = {}
        # 对于一些官方物品，应该有一个标准的 物品到text的map
        if items is None:
            for i in range(10):
                _key = "物品_" + str(i)
                _text = "物品_" + str(i) + "提交之后反馈的台词"
                item2text[_key] = _text
            return item2text
        else:
            for item in items:
                name = item["name"]
                text = item["text"]
                item2text[name] = text
            return item2text

    def check_conditions(self):
        current_conditions = self.current_step['conds']
        if len(current_conditions) == 0:
            return False

        ans = True

        for condition in current_conditions:
            condition_flag = False
            for item in condition:
                if item in self.status:
                    condition_flag = True
            if not condition_flag:
                return False

        return ans
                
    def get_item_response(self, item_name):
        if item_name in self.item_expand_name2name:
            item_name = self.item_expand_name2name[item_name]

        if item_name not in self.status:
            self.status.add(item_name)

        next_status_info = ""

        if self.check_conditions():
            print("进入下一阶段")
            next_index = self.current_index + 1
            if next_index < len(self.prompt_steps):
                self.current_index = next_index
                self.current_step = self.prompt_steps[self.current_index]
                next_status_info = "\n" + self.current_step["welcome_info"]
                self.status = set()

        if item_name in self.item2text:
            return self.item2text[item_name] + next_status_info
        elif item_name in self.item2cache_text:
            return self.item2cache_text[item_name] + next_status_info
        else:
            return self.generate_item_response(item_name) + next_status_info

    def generate_item_response(self, item_name):
        # generate( current_system_prompt, examples_current_conditsion, related_words(Rag), random_example  )
        # 1. realated_words:
        background_info = ""
        for step in self.prompt_steps:
            background_info += f"该游戏阶段的背景设定: {step['prompt']}\n"
            background_info += f"该阶段的欢迎语: {step['welcome_info']}\n"
        for item in self.items:
            background_info += f"对于该游戏阶段中的关键道具'{item['name']}'的回复是: {item['text']}\n"

        # 2. get current_system_prompt :

        current_system_prompt = self.get_system_prompt()

        system_prompt = f"""
        你的剧情设定如下:{current_system_prompt}\n
        这是游戏的背景信息和对剧情推动有关键作用的道具信息:{background_info}
        """
        user_prompt = f"""
        Let's think it step-by-step and output into JSON format，包括下列关键字
        "item_name" - 要针对输出的物品名称{item_name}
        "analysis" - 结合剧情判断剧情中的人物应该进行怎样的输出
        "echo" - 重复下列字符串: 我认为在剧情设定的人物眼里，看到物品 {item_name}时，会说
        "character_response" - 根据人物性格和剧情设定，输出人物对物品 {item_name} 的反应
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        response_text = get_llm_response(messages)

        response_in_dict = parse_json(response_text, forced_keywords=["character_response"])

        if response_in_dict is not None and "character_response" in response_in_dict:
            response_text = response_in_dict["character_response"]
        else:
            response_text = "这是什么？一张不知所云的图片。"

        return response_text

    def get_item_names(self):
        ans = []
        for item in self.items:
            ans.append(item["name"])
        return ans

    def get_welcome_info(self):
        return self.current_step["welcome_info"]
        # return "欢迎来到游戏，这是一个默认信息，之后应该随着GameMaster指定不同的游戏而改变。"

    def extract_object_from_image(self,resized_img):

        if self.use_record_images:
            try:
                feature = self.image_master.extract_feature(resized_img)
                results = self.image_master.extract_item_from_feature(feature)
            except:
                print("Warning！ 提取图片特征失败！")
                results = None

            # print("使用快速图片识别的开关已经打开")
            if results is not None and len(results) > 0:
                res = results[0]['name']
                similarity = results[0]['similarity']
                if similarity > self.record_image_threshold:
                    print("快速识别出物体为:", res)
                    return res

        # img_name为img的path路径
        candidate_object_list_names = self.get_item_names()
        str_response = get_vlm_response_cot(resized_img, candidate_object_list_names)
        # response = get_vlm_response(img_name, candidate_object_list_names)
        dict_response = parse_json(str_response, forced_keywords=["fixed_object_name","major_object"])
        print(dict_response)
        if dict_response is not None and "fixed_object_name" in dict_response:
            response_text = dict_response["fixed_object_name"]
        elif dict_response is not None and "major_object" in dict_response:
            response_text = dict_response["major_object"]
        else:
            response_text = "一张不知所云的图片。"

        return response_text


    def submit_image( self, img_name ):
        # 这里提交img是img_path
        object_name = self.extract_object_from_image(img_name)
        return self.submit_item( object_name )


    def submit_item(self, item_name):
        user_info = "用户提交了物品：" + item_name
        print(user_info)
        response_info = self.get_item_response(item_name)
        self.history.append( {"role": "user", "content": user_info} )
        self.history.append( {"role": "assistant", "content": response_info} )
        return user_info, response_info

    def get_chat_response(self, system_prompt, user_input):
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        max_history_len = min(6, len(self.history))
        for i in range( max_history_len):
            messages.append( self.history[-(max_history_len-i)] )

        messages.append({"role": "user", "content": user_input})
        response = get_llm_response(messages, max_tokens=400)
        self.history.append( {"role": "user", "content": user_input} )
        self.history.append( {"role": "assistant", "content": response} )
        return response

    def submit_chat(self, user_input):
        system_prompt = self.get_system_prompt()
        response = self.get_chat_response(system_prompt, user_input)
        return user_input, response

    def get_system_prompt(self, status = None):
        if status is None:
            status = self.status
        # 在我们的设计中， status是一个set的函数
        # 如果程序很良好的话 应该支持后期从config来配置status到prompt的逻辑
        # return "你是一个助手"
        return self.current_step["prompt"]

    # def get_chat_response(self, status, user_input):
    #     # 在我们的设计中， status是一个set的函数
    #     # 如果程序很良好的话 应该支持后期从config来配置status到prompt的逻辑
    #     return "你是一个助手"


    def get_status(self):
        # 把self.status转换成字符串返回
        if len(self.status) > 0:
            return "当前状态：" + ", ".join(self.status)
        else:
            return "当前状态：null"
            
if __name__ == '__main__':
    yaml_path = "config/police.yaml"
    gm = GameMaster(yaml_path)
    print("GameMaster初始化成功！")
    print("Prompt steps:", gm.prompt_steps)
    print("Items:", gm.items)
    print(gm.name2img_path('双节棍'))
    print(gm.generate_item_response("手机"))