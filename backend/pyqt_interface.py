import sys
import cv2
import os
import yaml
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QTextEdit, QLineEdit, QPushButton, QListWidget, 
                            QSplitter, QGroupBox, QFormLayout, QMessageBox, QScrollArea)
from PyQt5.QtGui import QPixmap, QImage, QFont, QKeySequence
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QAudioOutput
from src.GameMaster import GameMaster
from src.resize_img import resize_image
from src.fishTTS import get_audio

# 设置中文字体
font = QFont()
font.setFamily("SimHei")
font.setPointSize(10)

class CameraThread(QThread):
    frame_signal = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super(CameraThread, self).__init__(parent)
        self.running = False
        self.cap = None

    def load_config(self):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'pyqt_config.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config

    def run(self):
        self.running = True
        config = self.load_config()
        camera_id = config.get('camera_id', 0)
        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            QMessageBox.critical(None, "错误", "无法打开摄像头")
            self.running = False
            return

        while self.running:
            ret, frame = self.cap.read()
            if ret:
                # 转换为RGB格式
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # 转换为QImage
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.frame_signal.emit(q_image.scaled(640, 480, Qt.KeepAspectRatio))
            # 短暂休眠以减少CPU占用
            self.msleep(10)

    def stop(self):
        self.running = False
        if self.cap is not None:
            self.cap.release()
        self.wait()

class WhaleLandApp(QMainWindow):
    # 定义类级别的信号
    image_processed_signal = pyqtSignal(str, str, str)
    
    def __init__(self):
        super(WhaleLandApp, self).__init__()
        # 连接信号和槽
        self.image_processed_signal.connect(self.on_image_processed)
        self.init_ui()
        self.init_game()
        self.init_camera()
        self.init_audio()

    def init_ui(self):
        self.setWindowTitle("鲸娱秘境")
        self.setGeometry(100, 100, 1200, 800)

        # 主布局
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # 左侧聊天区域
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # 聊天标题
        title_label = QLabel("# 鲸娱秘境-MLLM结合线下密室的人工智能创新应用")
        title_label.setFont(QFont("SimHei", 14, QFont.Bold))
        left_layout.addWidget(title_label)

        subtitle_label = QLabel("欢迎大家在点评搜索\"鲸娱秘境\"，线上demo为游戏环节一部分，并加入多模态元素")
        subtitle_label.setFont(font)
        left_layout.addWidget(subtitle_label)

        # 聊天窗口
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(font)
        self.chat_display.setAcceptRichText(True)
        left_layout.addWidget(self.chat_display)

        # 消息输入区域
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setFont(font)
        self.message_input.setPlaceholderText("请输入您的消息...")
        self.send_button = QPushButton("发送")
        self.send_button.setFont(font)
        self.send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)

        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        left_layout.addLayout(input_layout)

        # 右侧功能区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # 摄像头区域
        camera_group = QGroupBox("摄像头")
        camera_layout = QVBoxLayout(camera_group)
        self.camera_label = QLabel("摄像头预览")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumSize(640, 480)
        camera_layout.addWidget(self.camera_label)

        # 拍照按钮
        self.capture_button = QPushButton("拍照 (Ctrl+P)")
        self.capture_button.setFont(font)
        self.capture_button.clicked.connect(self.capture_image)
        camera_layout.addWidget(self.capture_button)
        right_layout.addWidget(camera_group)

        # 物品选择区域
        item_group = QGroupBox("向NPC提交场景中的物品")
        item_layout = QVBoxLayout(item_group)
        self.item_list = QListWidget()
        self.item_list.setFont(font)
        self.item_submit_button = QPushButton("提交场景内的物品")
        self.item_submit_button.setFont(font)
        self.item_submit_button.clicked.connect(self.submit_item)

        item_layout.addWidget(self.item_list)
        item_layout.addWidget(self.item_submit_button)
        right_layout.addWidget(item_group)

        # 直接输入物品名区域
        direct_item_group = QGroupBox("直接输入物品名")
        direct_item_layout = QHBoxLayout(direct_item_group)
        self.direct_item_input = QLineEdit()
        self.direct_item_input.setFont(font)
        self.direct_item_submit = QPushButton("提交")
        self.direct_item_submit.setFont(font)
        self.direct_item_submit.clicked.connect(self.submit_direct_item)

        direct_item_layout.addWidget(self.direct_item_input)
        direct_item_layout.addWidget(self.direct_item_submit)
        right_layout.addWidget(direct_item_group)

        # 重置按钮
        self.reset_button = QPushButton("重置剧情")
        self.reset_button.setFont(font)
        self.reset_button.clicked.connect(self.reset_game)
        right_layout.addWidget(self.reset_button)

        # 状态显示区域
        status_group = QGroupBox("Agent状态显示")
        status_layout = QVBoxLayout(status_group)
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        self.status_display.setFont(font)
        self.status_display.setMaximumHeight(60)
        status_layout.addWidget(self.status_display)
        right_layout.addWidget(status_group)

        # 分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([700, 500])
        main_layout.addWidget(splitter)

        # 设置快捷键 (Ctrl+P 和 Enter)
        self.capture_button.setShortcut(QKeySequence("Ctrl+P, Return"))

    def init_game(self):
        yaml_path = "config/police.yaml"
        self.game_master = GameMaster(yaml_path)
        print("为线下demo启动 本地视觉 模型..")
        self.game_master.init_image_master()
        print("模型 启动！")
        self.update_item_list()
        welcome_info = self.game_master.get_welcome_info()
        self.append_to_chat("系统", welcome_info)
        self.update_status()

    def init_camera(self):
        self.camera_thread = CameraThread()
        self.camera_thread.frame_signal.connect(self.update_camera_frame)
        self.camera_thread.start()
        
    def init_audio(self):
        # 初始化音频播放器 (兼容旧版PyQt5)
        self.audio_player = QMediaPlayer()
        self.audio_player.setVolume(50)  # 设置音量为50%
        
    def generate_and_play_audio(self, text):
        # 生成音频并播放
        audio_path = get_audio(text)
        if audio_path and os.path.exists(audio_path):
            from PyQt5.QtMultimedia import QMediaContent
            self.audio_player.setMedia(QMediaContent(QUrl.fromLocalFile(audio_path)))
            self.audio_player.play()

    def update_camera_frame(self, image):
        self.camera_label.setPixmap(QPixmap.fromImage(image))
        self.current_frame = image



    def capture_image(self):
        if hasattr(self, 'current_frame'):
            # 保存图片到临时文件，添加时间戳避免覆盖
            import time
            timestamp = int(time.time())
            temp_path = f"temp_captured_image_{timestamp}.jpg"
            self.current_frame.save(temp_path)
            # 处理图片并异步提交
            resized_img_to_rec = resize_image(temp_path, max_height=400)
            resized_img = resize_image(temp_path, max_height=200)
            

                
            # 创建线程处理图片
            from PyQt5.QtCore import QThread, pyqtSignal
            class ImageProcessingThread(QThread):
                result_ready = pyqtSignal(str, str, str)
                
                def __init__(self, game_master, img_path, temp_path):
                    super().__init__()
                    self.game_master = game_master
                    self.img_path = img_path
                    self.temp_path = temp_path
                
                def run(self):
                    user_info, response = self.game_master.submit_image(self.img_path)
                    self.result_ready.emit(user_info, response, self.temp_path)

            # 启动线程
            self.img_thread = ImageProcessingThread(self.game_master, resized_img_to_rec, temp_path)
            self.img_thread.result_ready.connect(self.on_image_processed)
            self.img_thread.finished.connect(self.img_thread.deleteLater)
            self.img_thread.start()
        else:
            QMessageBox.warning(self, "警告", "未检测到摄像头画面")

    def on_image_processed(self, user_info, response, temp_path):
        # 显示在聊天窗口
        self.append_to_chat("你 (图片)", f"<img src='{temp_path}' width='200'>")
        self.append_to_chat("NPC", response)
        # 更新状态
        self.update_status()
        # 播放音频
        self.generate_and_play_audio(response)

    def update_item_list(self):
        item_names = self.game_master.get_item_names()
        self.item_list.clear()
        self.item_list.addItems(item_names)

    def send_message(self):
        message = self.message_input.text().strip()
        if message:
            user_input, bot_response = self.game_master.submit_chat(message)
            self.append_to_chat("你", user_input)
            self.append_to_chat("NPC", bot_response)
            self.message_input.clear()
            self.update_status()
            # 播放音频
            self.generate_and_play_audio(bot_response)

    def submit_item(self):
        selected_items = self.item_list.selectedItems()
        if selected_items:
            item_name = selected_items[0].text()
            user_info, response_info = self.game_master.submit_item(item_name)
            # 显示物品图片
            img_path = self.game_master.name2img_path(item_name)
            if img_path and os.path.exists(img_path):
                self.append_to_chat("你 (物品)", f"<img src='{img_path}' width='200'>")
            else:
                self.append_to_chat("你 (物品)", item_name)
            self.append_to_chat("NPC", response_info)
            self.update_status()
            # 播放音频
            self.generate_and_play_audio(response_info)
        else:
            QMessageBox.warning(self, "警告", "请先选择一个物品")

    def submit_direct_item(self):
        item_name = self.direct_item_input.text().strip()
        if item_name:
            user_info, response_info = self.game_master.submit_item(item_name)
            self.append_to_chat("你 (物品)", item_name)
            self.append_to_chat("NPC", response_info)
            self.direct_item_input.clear()
            self.update_status()
            # 播放音频
            self.generate_and_play_audio(response_info)
        else:
            QMessageBox.warning(self, "警告", "请输入物品名")

    def reset_game(self):
        self.game_master = GameMaster("config/police.yaml")
        self.update_item_list()
        welcome_info = self.game_master.get_welcome_info()
        self.chat_display.clear()
        self.append_to_chat("系统", welcome_info)
        self.update_status()

    def append_to_chat(self, sender, message):
        # 简单的HTML格式化
        if message.startswith("<img"):
            self.chat_display.append(f"<b>{sender}:</b><br>{message}<br>")
        else:
            self.chat_display.append(f"<b>{sender}:</b> {message}<br>")
        # 滚动到底部
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum())

    def update_status(self):
        current_status = self.game_master.get_status()
        self.status_display.setText(str(current_status))

    def closeEvent(self, event):
        # 停止摄像头线程
        self.camera_thread.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(font)
    window = WhaleLandApp()
    window.show()
    sys.exit(app.exec_())