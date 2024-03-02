 
import os
from .base_tts import BaseTTS
import soundfile as sf
from transformers import AutoProcessor, BarkModel
from utils import create_temp_file, is_valid_filename 


class BarkTTS(BaseTTS):

    USE_CUDA = os.getenv('USE_CUDA')

    def __generate_audio(self, model, processor, text, voice="v2/en_speaker_6"):
        random_filename = create_temp_file(".wav")
        inputs = processor(text.strip(), voice_preset=voice)
        if self.USE_CUDA == "true":
            inputs.to("cuda")
        audio_array = model.generate(**inputs)
        audio_array = audio_array.cpu().numpy().squeeze()
        sf.write(random_filename, audio_array,
                 samplerate=22050, subtype='PCM_24')
        return random_filename

    def generate_voices(self, script_file):
        processor = AutoProcessor.from_pretrained("suno/bark")
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
                        voice_file = self.__generate_audio(
                            audio_model, processor, voice_text)
                        emoji_voice_dict[voice_text] = voice_file
        return emoji_voice_dict
