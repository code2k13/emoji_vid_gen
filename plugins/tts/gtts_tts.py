from gtts import gTTS
from utils import create_temp_file, is_valid_filename 
import time
from .base_tts import BaseTTS
from cache import Cache 

class GTTSTTS(BaseTTS):

    _cache = Cache()

    def __generate_audio(self, text: str):
        tts = gTTS(text=text, lang='en')
        random_filename = create_temp_file(".mp3")
        tts.save(random_filename)
        self._cache.store_text(text, random_filename)
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
                        existing_file = self._cache.get_file_path(voice_text)
                        if existing_file:
                            emoji_voice_dict[voice_text] = existing_file
                            print(f"Loading asset for '{voice_text}' from cache.")
                            continue
                        voice_file = self.__generate_audio(voice_text)
                        # very bad hack :-(
                        time.sleep(1)
                        emoji_voice_dict[voice_text] = voice_file
        return emoji_voice_dict
