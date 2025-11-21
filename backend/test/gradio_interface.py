
import gradio as gr
from src.GameMaster import GameMaster
import os
from src.resize_img import resize_image, get_img_html
import base64
from io import BytesIO
from src.fishTTS import get_audio


yaml_path = "config/police.yaml"
game_master = GameMaster( yaml_path )
item_str_list = game_master.get_item_names()
welcome_info = game_master.get_welcome_info()


def callback_generate_audio( chatbot ):
    if len(chatbot) == 0:
        return None
    
    response_message = chatbot[-1][1]

    audio_path = get_audio(response_message)

    return gr.update( value = audio_path , autoplay = True )


def chat_submit_callback(user_message, chat_history):
    # 调用GameMaster的submit_chat方法获取用户消息和回复
    user_input, bot_response = game_master.submit_chat(user_message)
    # 将对话记录添加到聊天历史
    chat_history.append((user_input, bot_response))
    return chat_history, ""

# 修改chat_submit_callback或新增item_submit_callback
def item_submit_callback(item_name, chat_history):
    # print( item_name )
    if not item_name.strip() or item_name.strip() == "":
        return chat_history, ""
    # 调用GameMaster的submit_item方法获取用户消息和回复
    user_info, response_info = game_master.submit_item(item_name)

    img_path = game_master.name2img_path(item_name)

    if img_path is not None and os.path.exists(img_path):
        # print(img_path)
        # user_info = gr.Image(resize_image(img_path,max_height=200))
        resized_img = resize_image(img_path, max_height=200)
        img_html = get_img_html(resized_img)
        user_info = gr.HTML(img_html)

    # 将对话记录添加到聊天历史
    chat_history.append((user_info, response_info))
    return chat_history, ""


def img_submit_callback( image_input, chatbot):
    '''
    参考item_submit_callback
    这里会先把图片resize到max_height = 200
    response = ”你上传了一张图片 我们正在编写VLM识别图片的功能“
    然后增加信息(resized_img, resposne)
    '''
    if image_input:
        resized_img_to_rec = resize_image(image_input, max_height=400)
        resized_img = resize_image(image_input, max_height=200)
        img_html = get_img_html(resized_img)
        # response = "你上传了一张图片 我们正在编写VLM识别图片的功能"
        user_info, response = game_master.submit_image(resized_img_to_rec)
        chatbot.append((gr.HTML(img_html), response))
    return chatbot

def update_status_show():
    current_status = game_master.get_status()
    return current_status


css = """
.chatbot img {
    max-height: 200px !important;
    width: auto !important;
}"""

with gr.Blocks(title="鲸娱秘境-Intel参赛", css=css) as demo:
    with gr.Tabs() as tabs:
        with gr.TabItem("demo"):
            gr.Markdown("# 鲸娱秘境-英特尔人工智能创新应用")
            gr.Markdown('欢迎大家在点评搜索"鲸娱秘境",线上demo为游戏环节一部分，并加入多模态元素')
            with gr.Row():
                # 左侧ChatBox列
                with gr.Column(scale=2):  # 占2份宽度
                    chatbot = gr.Chatbot(label="对话窗口", height=800, value=[(None, welcome_info)])
                    # 添加聊天输入框和发送按钮
                    user_input = gr.Textbox(label="输入消息", placeholder="请输入您的消息...", interactive=True)
                    send_btn = gr.Button("发送", variant="primary")

                # 右侧操作列
                with gr.Column(scale=1):  # 占1份宽度

                    # 第二行：单选框 + 提交按钮
                    with gr.Row():  # 让单选框和按钮在同一行
                        radio_choices = gr.Radio(label="向NPC提交场景中的物品", choices= item_str_list, 
                                              value="生成描述", interactive=True)

                    with gr.Row():
                        item_submit_btn = gr.Button("提交场景内的物品", variant="primary")

                    # 第一行：图片上传（支持文件和摄像头）
                    image_input = gr.Image(type="filepath", label="上传图片")

                    with gr.Row():  # 让单选框和按钮在同一行
                        img_submit_btn = gr.Button("提交图片中的物品", variant="primary")


                    with gr.Row():
                        reload_btn = gr.Button("重置剧情", variant="primary")

                    with gr.Row():
                        audio_player = gr.Audio()

                    # 创建一个折叠面板，初始状态为关闭
                    with gr.Accordion("For debug", open=False):
                        with gr.Row():
                            item_text_to_submit = gr.Textbox(label="直接输入物品名", value="", interactive=True, scale = 20)
                            item_text_submit_btn = gr.Button("提交", variant="primary", scale = 1)
                        
                        current_status = game_master.get_status()
                        status_display = gr.Textbox(label="agent状态显示", value= current_status, 
                                                interactive=False, max_lines=3)

                    
                    

            # 添加消息处理函数
            def send_message(user_message, chat_history):
                if user_message.strip():
                    chat_history.append((user_message, "正在处理您的请求..."))
                    return "", chat_history
                return user_message, chat_history

            # 绑定事件处理
            send_btn.click(chat_submit_callback, [user_input, chatbot], [chatbot, user_input])
            user_input.submit(chat_submit_callback, [user_input, chatbot], [chatbot, user_input])

            img_submit_btn.click(
                fn = img_submit_callback,
                inputs = [image_input, chatbot],
                outputs = [chatbot]
            ).then(
                fn=update_status_show,
                inputs=[],
                outputs=[status_display]
            ).then(
                fn = callback_generate_audio,
                inputs=[ chatbot],
                outputs=[audio_player]
            )


            # 绑定物品提交按钮事件
            item_submit_btn.click(
                fn=item_submit_callback,
                inputs=[radio_choices, chatbot],
                outputs=[chatbot, radio_choices]
            ).then(
                fn=update_status_show,
                inputs=[],
                outputs=[status_display]
            ).then(
                fn=callback_generate_audio,
                inputs = [chatbot],
                outputs = [audio_player]
            )

            item_text_submit_btn.click(
                fn=item_submit_callback,
                inputs=[item_text_to_submit, chatbot],
                outputs=[chatbot, item_text_to_submit]
            ).then(
                fn=update_status_show,
                inputs=[],
                outputs=[status_display]
            ).then(
                fn=callback_generate_audio,
                inputs = [chatbot],
                outputs = [audio_player]
            )

            # 绑定刷新按钮事件
            def reload_game():
                global game_master
                game_master = GameMaster(yaml_path)
                return [(None,game_master.get_welcome_info())], game_master.get_status()
                
            reload_btn.click(
                fn=reload_game,
                inputs=[],
                outputs=[chatbot, status_display]
            )
        with gr.TabItem("Readme"):
            with open("demo_info.md", "r", encoding="utf-8") as f:
                readme_content = f.read()
            gr.Markdown(readme_content)

if __name__ == "__main__":
    demo.launch(share=True)

