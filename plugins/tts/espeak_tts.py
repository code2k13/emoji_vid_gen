import pyttsx3
from utils import create_temp_file, is_valid_filename 
import time
from .base_tts import BaseTTS
 

class ESpeakTTS(BaseTTS):

    def __generate_audio(self, text: str):
        engine = pyttsx3.init()
        random_filename = create_temp_file(".mp3")
        engine.setProperty("rate", 120)
        engine.save_to_file(text, random_filename)
        engine.runAndWait()
        return random_filename

    def generate_voices(self, script_file: str):
        emoji_voice_dict = {}
        with open(script_file, 'r') as f:
            for line in f:
                if not line.startswith("Audio:") and not line.startswith("Image:") and not line.startswith("Title:") and ":" in line:
                    voice_text = line.split(":")[1].strip()
                    if is_valid_filename(voice_text):
                        emoji_voice_dict[voice_text] = voice_text
                    else:
                        voice_file = self.__generate_audio(voice_text)
                        # very bad hack :-(
                        time.sleep(1)
                        emoji_voice_dict[voice_text] = voice_file
        return emoji_voice_dict
