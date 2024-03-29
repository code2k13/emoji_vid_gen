 
import os
from .base_tts import BaseTTS
import soundfile as sf
from transformers import AutoProcessor, BarkModel
from utils import create_temp_file, is_valid_filename 
from cache import Cache


class BarkTTS(BaseTTS):

    USE_CUDA = os.getenv('USE_CUDA')
    _cache = Cache()

    def __generate_audio(self, model, processor, text, voice="v2/en_speaker_6"):
        random_filename = create_temp_file(".wav")
        inputs = processor(text.strip(), voice_preset=voice, return_tensors="pt")
        if self.USE_CUDA == "true":
            inputs.to("cuda")
        audio_array = model.generate(**inputs,do_sample=True)
        audio_array = audio_array.cpu().numpy().squeeze()
        sf.write(random_filename, audio_array,
                 samplerate=22050, subtype='PCM_24')
        self._cache.store_text(text,random_filename)
        return random_filename

    def generate_voices(self, script_file):
        processor = AutoProcessor.from_pretrained("suno/bark-small")
        audio_model = BarkModel.from_pretrained("suno/bark-small")
        if self.USE_CUDA == "true":
            audio_model.to("cuda")
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

                        voice_file = self.__generate_audio(
                            audio_model, processor, voice_text)
                        emoji_voice_dict[voice_text] = voice_file
        return emoji_voice_dict
