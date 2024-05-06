from .base_tts import BaseTTS
from openai import OpenAI
from rich.console import Console
from utils.helpers import create_temp_file, is_valid_filename
from utils.cache import Cache
from typing import Literal


class OpenAI_TTS(BaseTTS):
    _cache = Cache()

    def __init__(self, config):
        super().__init__(config)
        self.console = Console()
        self._validate()

    def _validate(self):
        tts_config = self.config['text_to_speech']
        if 'voice' not in tts_config:
            self.voice: Literal['alloy', 'echo', 'fable',
                                'onyx', 'nova', 'shimmer'] = 'alloy'
        else:
            self.voice: Literal['alloy', 'echo', 'fable', 'onyx',
                                'nova', 'shimmer'] = tts_config['voice'].lower()
        if 'model' not in tts_config:
            self.model = 'tts-1'
        else:
            self.model = tts_config['model']

        if 'request_delay_sec' in tts_config:
            self.request_delay_sec = int(tts_config['request_delay_sec'])
        else:
            self.console.print(
                "[grey] Using default delay of 6 seconds for openai tts requests")
            self.request_delay_sec = 6

    def __generate_audio(self, text, voice):
        try:
            random_filename = create_temp_file(".mp3")
            client = OpenAI()
            with client.audio.speech.with_streaming_response.create(model=self.model, voice=voice, input=text) as response:
                response.stream_to_file(random_filename)
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
                    voice, _ = self.get_character_data(line)
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
                        if not voice:
                            voice = self.voice
                        voice_file = self.__generate_audio(voice_text, voice)
                        emoji_voice_dict[voice_text] = voice_file
        return emoji_voice_dict
