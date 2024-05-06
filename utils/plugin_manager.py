import yaml
from plugins.tts.openai_tts import OpenAI_TTS
from plugins.txt2img.openai_txt2img import OpenAI_Txt2Img
from plugins.txt2img.sdturbo_txt2img import StableDiffusionTxt2Img
from plugins.txt2dialog.default_txt2dialog import DefaultTxt2Dialog
from plugins.tts.bark_tts import BarkTTS
from plugins.tts.espeak_tts import ESpeakTTS
from plugins.txt2audio.audio_ldm_txt2audio import AudioLDMTxt2Audio
from plugins.tts.elevenlabs_tts import ElevenLabsTTS
from plugins.tts.parler_tts import ParlerTTS
 

class PluginManager:
    def __init__(self, file_path):
        self.config = self.load_config(file_path)

    def load_config(self, file_path):
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)

    def get_text_to_image_model(self):
        text_to_image_config = self.config.get('text_to_image', {})
        provider = text_to_image_config.get('provider', None)

        if provider == 'hf_text2image':
            return StableDiffusionTxt2Img(self.config)
        elif provider == 'openai':
            return OpenAI_Txt2Img(self.config)
        else:
            raise ValueError(f"Unsupported provider '{provider}' for text_to_image.")

    def get_text_to_speech_model(self):
        text_to_speech_config = self.config.get('text_to_speech', {})
        provider = text_to_speech_config.get('provider', None)

        if provider == 'bark':
            return BarkTTS(self.config)
        elif provider == 'espeak':
            return ESpeakTTS(self.config)
        elif provider == 'elevenlabs':
            return ElevenLabsTTS(self.config)
        elif provider == 'openai':
            return OpenAI_TTS(self.config)
        elif provider == 'parler':
            return ParlerTTS(self.config)
        else:
            raise ValueError(f"Unsupported provider '{provider}' for text_to_speech.")

    def get_text_to_dialog_model(self):
        text_to_dialog_config = self.config.get('text_to_dialog', {})
        provider = text_to_dialog_config.get('provider', None)

        if provider == 'default_txt2dialog':
            return DefaultTxt2Dialog(self.config)
        else:
            raise ValueError(f"Unsupported provider '{provider}' for text_to_dialog.")

    def get_text_to_audio_model(self):
        text_to_audio_config = self.config.get('text_to_audio', {})
        provider = text_to_audio_config.get('provider', None)

        if provider == 'hf_audioldm':
            return AudioLDMTxt2Audio(self.config)
        else:
            raise ValueError(f"Unsupported provider '{provider}' for text_to_audio.")