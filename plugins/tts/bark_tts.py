
from .base_tts import BaseTTS
import soundfile as sf
from transformers import AutoProcessor, BarkModel
from utils.helpers import create_temp_file, is_valid_filename
from utils.cache import Cache
from rich.console import Console


class BarkTTS(BaseTTS):

    _cache = Cache()

    def __init__(self, config):
        super().__init__(config)
        self.__validate()

    def __validate(self):
        console = Console()
        if 'text_to_speech' in self.config:
            tts_config = self.config['text_to_speech']
            if 'model' not in tts_config:
                self.model = 'suno/bark-small'
            elif tts_config['model'] != 'suno/bark-small':
                console.print(
                    "[bold red]Error:[/bold red] 'suno/bark-small' is the only supported 'model' for 'bark' TTS provider.")
                raise ValueError("Invalid 'model' specified in config.")
            else:
                self.model = tts_config['model']
            if 'voice' not in tts_config:
                self.voice = 'v2/en_speaker_6'
            else:
                self.voice = tts_config["voice"]

    def __generate_audio(self, model, processor, text, voice):
        random_filename = create_temp_file(".wav")
        inputs = processor(text.strip(), voice_preset=voice,
                           return_tensors="pt")
        if self.use_cuda:
            inputs.to("cuda")
        audio_array = model.generate(**inputs, do_sample=True)
        audio_array = audio_array.cpu().numpy().squeeze()
        sf.write(random_filename, audio_array,
                 samplerate=22050, subtype='PCM_24')
        self._cache.store_text(text, random_filename)
        return random_filename

    def generate_voices(self, script_file):
        console = Console()
        processor = AutoProcessor.from_pretrained(self.model)
        audio_model = BarkModel.from_pretrained(self.model)
        if self.use_cuda:
            audio_model.to("cuda")
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
                            
                        voice_file = self.__generate_audio(
                            audio_model, processor, voice_text, voice)
                        emoji_voice_dict[voice_text] = voice_file
        return emoji_voice_dict
