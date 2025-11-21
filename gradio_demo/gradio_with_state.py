import gradio as gr
from src.GameMaster import GameMaster
import os
from src.resize_img import resize_image, get_img_html
from src.fishTTS import get_audio

yaml_path = "config/police.yaml"

def create_game_master():
    return GameMaster(yaml_path)

class SessionState:
    def __init__(self):
        self.game_master = create_game_master()
        self.item_str_list = self.game_master.get_item_names()
        self.welcome_info = self.game_master.get_welcome_info()

def callback_generate_audio(chatbot):
    if len(chatbot) == 0:
        return None
    response_message = chatbot[-1][1]
    audio_path = get_audio(response_message)
    return gr.update(value=audio_path, autoplay=True)

def chat_submit_callback(user_message, chat_history, state: SessionState):
    if user_message.strip():
        user_input, bot_response = state.game_master.submit_chat(user_message)
        chat_history.append((user_input, bot_response))
    return chat_history, ""

def item_submit_callback(item_name, chat_history, state: SessionState):
    if not item_name.strip():
        return chat_history, ""
    user_info, response_info = state.game_master.submit_item(item_name)
    img_path = state.game_master.name2img_path(item_name)
    if img_path and os.path.exists(img_path):
        resized_img = resize_image(img_path, max_height=200)
        img_html = get_img_html(resized_img)
        user_info = gr.HTML(img_html)
    chat_history.append((user_info, response_info))
    return chat_history, ""

def img_submit_callback(image_input, chatbot, state: SessionState):
    if image_input:
        resized_img_to_rec = resize_image(image_input, max_height=400)
        resized_img = resize_image(image_input, max_height=200)
        img_html = get_img_html(resized_img)
        user_info, response = state.game_master.submit_image(resized_img_to_rec)
        chatbot.append((gr.HTML(img_html), response))
    return chatbot

def update_status_show(state: SessionState):
    return state.game_master.get_status()

def reload_game(state: SessionState):
    state.game_master = create_game_master()
    return [(None, state.game_master.get_welcome_info())], state.game_master.get_status()

css = """
.chatbot img {
    max-height: 200px !important;
    width: auto !important;
}"""

with gr.Blocks(title="鲸娱秘境", css=css) as demo:
    state = gr.State(SessionState())
    
    with gr.Tabs() as tabs:
        with gr.TabItem("demo"):
            gr.Markdown("# 鲸娱秘境-MLLM结合线下密室的人工智能创新应用")
            gr.Markdown('欢迎大家在点评搜索"鲸娱秘境",线上demo为游戏环节一部分，并加入多模态元素')

            with gr.Row():
                with gr.Column(scale=2):
                    
                    chatbot = gr.Chatbot(label="对话窗口", height=800, value=lambda: [(None, state.value.welcome_info)] if hasattr(state, 'value') else [(None, "")])
                    user_input = gr.Textbox(label="输入消息", placeholder="请输入您的消息...", interactive=True)
                    send_btn = gr.Button("发送", variant="primary")
                
                with gr.Column(scale=1):
                    with gr.Row():
                        radio_choices = gr.Radio(label="向NPC提交场景中的物品", 
                                              choices=[],
                                              value="生成描述", interactive=True)
                    
                    with gr.Row():
                        item_submit_btn = gr.Button("提交场景内的物品", variant="primary")
                    
                    image_input = gr.Image(type="filepath", label="上传图片")
                    
                    with gr.Row():
                        img_submit_btn = gr.Button("提交图片中的物品", variant="primary")
                    
                    with gr.Row():
                        reload_btn = gr.Button("重置剧情", variant="primary")
                    
                    with gr.Row():
                        audio_player = gr.Audio()
                    
                    with gr.Accordion("For debug", open=False):
                        with gr.Row():
                            item_text_to_submit = gr.Textbox(label="直接输入物品名", value="", interactive=True, scale=20)
                            item_text_submit_btn = gr.Button("提交", variant="primary", scale=1)
                        
                        status_display = gr.Textbox(label="agent状态显示", interactive=False, max_lines=3)
            
            send_btn.click(chat_submit_callback, [user_input, chatbot, state], [chatbot, user_input])
            user_input.submit(chat_submit_callback, [user_input, chatbot, state], [chatbot, user_input])
            
            img_submit_btn.click(
                fn=img_submit_callback,
                inputs=[image_input, chatbot, state],
                outputs=[chatbot]
            ).then(
                fn=update_status_show,
                inputs=[state],
                outputs=[status_display]
            ).then(
                fn=callback_generate_audio,
                inputs=[chatbot],
                outputs=[audio_player]
            )
            
            item_submit_btn.click(
                fn=item_submit_callback,
                inputs=[radio_choices, chatbot, state],
                outputs=[chatbot, radio_choices]
            ).then(
                fn=update_status_show,
                inputs=[state],
                outputs=[status_display]
            ).then(
                fn=callback_generate_audio,
                inputs=[chatbot],
                outputs=[audio_player]
            )
            
            item_text_submit_btn.click(
                fn=item_submit_callback,
                inputs=[item_text_to_submit, chatbot, state],
                outputs=[chatbot, item_text_to_submit]
            ).then(
                fn=update_status_show,
                inputs=[state],
                outputs=[status_display]
            ).then(
                fn=callback_generate_audio,
                inputs=[chatbot],
                outputs=[audio_player]
            )
            
            reload_btn.click(
                fn=reload_game,
                inputs=[state],
                outputs=[chatbot, status_display]
            )
            
            def update_radio_choices(state: SessionState):
                return gr.update(choices=state.item_str_list)
            
            demo.load(
                fn=update_radio_choices,
                inputs=[state],
                outputs=[radio_choices]
            )
            
            def update_chatbot(state: SessionState):
                return gr.update(value=[(None, state.welcome_info)])
            
            demo.load(
                fn=update_chatbot,
                inputs=[state],
                outputs=[chatbot]
            )
        
        with gr.TabItem("Readme"):
            with open("demo_info.md", "r", encoding="utf-8") as f:
                readme_content = f.read()
            gr.Markdown(readme_content)

if __name__ == "__main__":
    demo.launch(share=True)