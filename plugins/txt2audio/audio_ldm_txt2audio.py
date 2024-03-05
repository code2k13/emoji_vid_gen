from utils import create_temp_file, is_valid_filename
from .base_txt2audio import BaseText2Audio
import scipy
from diffusers import AudioLDMPipeline
import os
from cache import Cache


class AudioLDMTxt2Audio(BaseText2Audio):

    USE_CUDA = os.getenv('USE_CUDA')
    _cache = Cache()

    def __generate_audio_effect(self, model, text: str):
        random_filename = create_temp_file(".wav")
        audio = model(text, num_inference_steps=10,
                      audio_length_in_s=5.0).audios[0]
        scipy.io.wavfile.write(random_filename, rate=16000, data=audio)
        self._cache.store_text(text, random_filename)
        return random_filename

    def generate_audio(self, script_file: str):
        repo_id = "cvssp/audioldm-m-full"
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
                            print(f"Loading asset for '{text}' from cache.")
                            continue
                        if not audio_effect_model:
                            audio_effect_model = AudioLDMPipeline.from_pretrained(
                                repo_id)
                            if self.USE_CUDA == "true":
                                audio_effect_model.to("cuda")
                        audio_file_path = self.__generate_audio_effect(
                            audio_effect_model, text)
                        audio_dict[text] = audio_file_path
        return audio_dict
