from utils.helpers import create_temp_file, is_valid_filename
from .base_txt2audio import BaseText2Audio
import scipy
from diffusers import AudioLDMPipeline
import os
from utils.cache import Cache
from rich.console import Console

class AudioLDMTxt2Audio(BaseText2Audio):

    _cache = Cache()

    def __init__(self, config):
        super().__init__(config)
        self.__validate()

    def __validate(self):
        console = Console()
        if 'text_to_audio' in self.config:
            tta_config = self.config['text_to_audio']
            default_model = 'cvssp/audioldm-m-full'
            if 'model' not in tta_config:
                self.model = default_model
            elif tta_config['model'] != default_model:
                console.print(
                    f"[bold red]Error:[/bold red] '{default_model}' is the only supported 'model' for 'hf_audioldm' provider.")
                raise ValueError("Invalid 'model' specified in config.")
            else:
                self.model = tta_config['model']

    def __generate_audio_effect(self, model, text: str):
        random_filename = create_temp_file(".wav")
        audio = model(text, num_inference_steps=10,
                      audio_length_in_s=5.0).audios[0]
        scipy.io.wavfile.write(random_filename, rate=16000, data=audio)
        self._cache.store_text(text, random_filename)
        return random_filename

    def generate_audio(self, script_file: str):
        console = Console()
        repo_id = self.model
        audio_effect_model = None
        audio_dict = {}
        with open(script_file, 'r') as f:
            for line in f:
                if line.startswith("Audio:"):
                    text = line.split(":")[1].strip()
                    if is_valid_filename(text):
                        audio_dict[text] = text
                    else:
                        existing_file = self._cache.get_file_path(text)
                        if existing_file:
                            audio_dict[text] = existing_file
                            console.print(f"[green]Loading asset for '{text}' from cache.")
                            continue
                        if not audio_effect_model:
                            audio_effect_model = AudioLDMPipeline.from_pretrained(
                                repo_id)
                            if self.use_cuda:
                                audio_effect_model.to("cuda")
                        audio_file_path = self.__generate_audio_effect(
                            audio_effect_model, text)
                        audio_dict[text] = audio_file_path
        return audio_dict
