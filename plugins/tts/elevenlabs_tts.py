from .base_tts import BaseTTS
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from rich.console import Console
from utils.helpers import create_temp_file, is_valid_filename
from utils.cache import Cache

class ElevenLabsTTS(BaseTTS):
    _cache = Cache()

    def __init__(self, config):
        super().__init__(config)
        self.client = ElevenLabs(api_key=self.config.get('api_key'))
        self.console = Console()
        self._validate()

    def _validate(self):        
        tts_config = self.config['text_to_speech']
        if 'voice' not in tts_config:
            self.voice = 'Rachel' 
        else:
            self.voice = tts_config['voice']
        if 'model' not in tts_config:
            self.model = 'eleven_multilingual_v2' 
        else:
            self.model = tts_config['model']


    def __generate_audio(self, text):
        try:
            random_filename = create_temp_file(".mp3")
            audio = self.client.generate(text=text, voice=self.voice, model=self.model)
            save(audio,random_filename)
            self._cache.store_text(text, random_filename)
            return random_filename
        except Exception as e:
            self.console.print(f"[bold red]Error:[/bold red] {e}")
            return None

    def generate_voices(self, script_file):
        console = Console()      
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
                            console.print(f"[green]Loading asset for '{
                                          voice_text}' from cache.")
                            continue

                        voice_file = self.__generate_audio(voice_text)
                        emoji_voice_dict[voice_text] = voice_file
        return emoji_voice_dict