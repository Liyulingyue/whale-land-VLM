from pathlib import Path
from dotenv import load_dotenv
import os
import json
from openai import OpenAI
import time

class FishTTS:
    def __init__(self, 
                 model="fishaudio/fish-speech-1.5",
                 voice="fishaudio/fish-speech-1.5:david",
                 speed=1.0,
                 output_format="mp3"):
        """
        Initialize the FishTTS instance
        
        Args:
            model (str): The model to use for TTS
            voice (str): The voice to use
            speed (float): Speech speed (0.5-2.0)
            output_format (str): Audio format (mp3/wav/pcm/opus)
        """
        load_dotenv()
        
        # Set proxy if needed
        # os.environ['HTTP_PROXY'] = 'http://localhost:8234'
        # os.environ['HTTPS_PROXY'] = 'http://localhost:8234'
        
        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=os.getenv('SILICONFLOW_API_KEY'),
            base_url="https://api.siliconflow.cn/v1"
        )
        
        # Store parameters
        self.model = model
        self.voice = voice
        self.speed = speed
        self.output_format = output_format
        
        # Ensure output directory exists
        self.output_dir = Path("local_data/temp_fish_tts")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.cache_text2audio = {}

        # 加载缓存文件
        self._load_cache()

        # clean the output directory, remove all temp files
        # for file in self.output_dir.glob("*"):
        #     file.unlink()

    def generate_audio_with_memory(self, text):
        '''
        如果 self.cache_text2audio 为空，则会尝试读取output_dir下的 cache.jsonl， 里面记录了过往生成过的text 和 audio_path
        如果text命中cache_text2audio，则直接返回audio_path
        如果没有命中，调用generate_audio生成新的audio，并更新cache_text2audio，更新cache.jsonl
        '''
        # 检查缓存是否已加载
        if not self.cache_text2audio:
            self._load_cache()

        # 检查文本是否在缓存中
        if text in self.cache_text2audio:
            return self.cache_text2audio[text]

        # 未命中缓存，生成新音频
        output_path = self.generate_audio(text)

        # 更新缓存
        self.cache_text2audio[text] = output_path
        self._save_cache_entry(text, output_path)

        return output_path
        
        
    def generate_audio(self, text):
        """
        Generate audio file from text
        
        Args:
            text (str): Text to convert to speech
            
        Returns:
            str: Path to generated audio file
        """
        # Generate unique filename using timestamp
        timestamp = int(time.time() * 1000)
        file_name = f"tts_{timestamp}.{self.output_format}"
        output_path = self.output_dir / file_name
        
        # Generate audio
        with self.client.audio.speech.with_streaming_response.create(
            model=self.model,
            voice=self.voice,
            input=text,
            speed=self.speed,
            response_format=self.output_format
        ) as response:
            response.stream_to_file(str(output_path))
            
        return str(output_path)

    def _load_cache(self):
        '''从cache.jsonl加载缓存''' 
        cache_file = self.output_dir / 'cache.jsonl'
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        self.cache_text2audio[entry['text']] = entry['audio_path']

    def _save_cache_entry(self, text, audio_path):
        '''将新条目保存到cache.jsonl''' 
        cache_file = self.output_dir / 'cache.jsonl'
        with open(cache_file, 'a', encoding='utf-8') as f:
            json.dump({'text': text, 'audio_path': audio_path}, f, ensure_ascii=False)
            f.write('\n')

# Global TTS instance
__fish_tts = None

def get_audio(text):
    """
    Get audio using global TTS instance
    
    Args:
        text (str): Text to convert to speech
        
    Returns:
        str: Path to generated audio file
    """
    global __fish_tts
    
    # Initialize if needed
    if __fish_tts is None:
        __fish_tts = FishTTS()
    
    return __fish_tts.generate_audio_with_memory(text)



if __name__ == "__main__":
    # Test direct class usage
    # tts = FishTTS()
    # file_path = tts.generate_audio("你好，这是一个测试。")
    # print(f"Generated audio file (direct): {file_path}")
    
    # Test global function
    file_path = get_audio("这是一段测试的音频")
    print(f"Generated audio file (global): {file_path}")

    # from play_audios import AudioPlayer
    # audio_player = AudioPlayer()
    # audio_player.play_audios([file_path])

    # remove generated audio file
    # os.remove(file_path)

    # Test with different parameters
    # custom_tts = FishTTS(speed=0.9, output_format="wav")
    # file_path = custom_tts.generate_audio("这是一个快速语音测试。")
    # print(f"Generated audio file (custom): {file_path}")