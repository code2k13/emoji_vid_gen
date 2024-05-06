import unittest
from unittest.mock import mock_open, patch

from plugins.txt2img.openai_txt2img import OpenAI_Txt2Img
from plugins.txt2img.sdturbo_txt2img import StableDiffusionTxt2Img
from plugins.txt2dialog.default_txt2dialog import DefaultTxt2Dialog
from plugins.tts.bark_tts import BarkTTS
from plugins.tts.espeak_tts import ESpeakTTS
from plugins.tts.openai_tts import OpenAI_TTS
from plugins.tts.parler_tts import ParlerTTS
from plugins.txt2audio.audio_ldm_txt2audio import AudioLDMTxt2Audio
from utils.plugin_manager import PluginManager


class TestPluginManager(unittest.TestCase):

    def setUp(self):
        self.plugin_manager = PluginManager('tests/test_preset/preset.yaml')

    def test_load_config(self):
        test_yaml = """
        text_to_image:
          provider: hf_text2image
        text_to_speech:
          provider: bark
        text_to_dialog:
          provider: default_txt2dialog
        text_to_audio:
          provider: hf_audioldm
        """
        with patch('builtins.open', mock_open(read_data=test_yaml)) as mock_file:
            manager  = PluginManager('fake_file.yaml')
            config = manager.config
            mock_file.assert_called_once_with('fake_file.yaml', 'r')
            self.assertEqual(config['text_to_image']['provider'], 'hf_text2image')

    def test_get_text_to_image_model(self):
        self.plugin_manager.config.update({'text_to_image': {'provider': 'hf_text2image'}})
        model = self.plugin_manager.get_text_to_image_model()
        self.assertIsInstance(model, StableDiffusionTxt2Img)

    def test_get_text_to_speech_model_bark(self):
        self.plugin_manager.config.update({'text_to_speech': {'provider': 'bark'}})
        model = self.plugin_manager.get_text_to_speech_model()
        self.assertIsInstance(model, BarkTTS)

    def test_get_text_to_speech_model_espeak(self):
        self.plugin_manager.config.update({'text_to_speech': {'provider': 'espeak'}})
        model = self.plugin_manager.get_text_to_speech_model()
        self.assertIsInstance(model, ESpeakTTS)

    def test_get_text_to_dialog_model(self):
        self.plugin_manager.config.update({'text_to_dialog': {'provider': 'default_txt2dialog'}})
        model = self.plugin_manager.get_text_to_dialog_model()
        self.assertIsInstance(model, DefaultTxt2Dialog)

    def test_get_text_to_audio_model(self):
        self.plugin_manager.config.update({'text_to_audio': {'provider': 'hf_audioldm'}})
        model = self.plugin_manager.get_text_to_audio_model()
        self.assertIsInstance(model, AudioLDMTxt2Audio)

    def test_get_text_to_speech_model_openai(self):
        self.plugin_manager.config.update({'text_to_speech': {'provider': 'openai'}})
        model = self.plugin_manager.get_text_to_speech_model()
        self.assertIsInstance(model, OpenAI_TTS)

    def test_get_text_to_speech_model_parler(self):
        self.plugin_manager.config.update({'text_to_speech': {'provider': 'parler'}})
        model = self.plugin_manager.get_text_to_speech_model()
        self.assertIsInstance(model, ParlerTTS)

    def test_get_text_to_image_model_openai(self):
        self.plugin_manager.config.update({'text_to_image': {'provider': 'openai'}})
        model = self.plugin_manager.get_text_to_image_model()
        self.assertIsInstance(model, OpenAI_Txt2Img)

if __name__ == '__main__':
    unittest.main()
