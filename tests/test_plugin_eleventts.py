from unittest.mock import patch, MagicMock, call
import unittest
import utils
import elevenlabs
from plugins.tts.elevenlabs_tts import ElevenLabsTTS


class TestElevenLabsTTS(unittest.TestCase):

    def setUp(self):
        self.config = {"global": {"width": 100, "height": 100,
                                  "use_cuda": "true"},  "text_to_speech": {"provider": "elevenlabs", "voice": "Glinda"}}
        self.tts = ElevenLabsTTS(self.config)

    def test_init(self):
        self.assertEqual(self.tts.config, self.config)
        self.assertEqual(self.tts.voice, "Glinda")
        self.assertEqual(self.tts.model, "eleven_multilingual_v2")

    def test_default_voice(self):
        config = {"global": {"width": 100, "height": 100,
                             "use_cuda": "true"},  "text_to_speech": {"provider": "elevenlabs", "model": "test_model"}}
        tts = ElevenLabsTTS(config)
        self.assertEqual(tts.voice, "Rachel")
        self.assertEqual(tts.model, "test_model")

    @patch('builtins.open', unittest.mock.mock_open(read_data="Audio:\nTitle:Title1\n🐿️:Text1"))
    @patch('plugins.tts.elevenlabs_tts.is_valid_filename', lambda x: False)
    @patch('plugins.tts.elevenlabs_tts.Cache.get_file_path', lambda x, y:  None)
    @patch('plugins.tts.elevenlabs_tts.Cache.store_text', lambda x, y, z:  None)
    @patch('plugins.tts.elevenlabs_tts.create_temp_file', lambda x: "mock_filename.mp3")
    @patch("plugins.tts.elevenlabs_tts.ElevenLabs.generate")
    @patch("plugins.tts.elevenlabs_tts.save")
    def test_generate_voices(self,  mock_save, mock_generate):
        config = {"global": {"width": 100, "height": 100,
                             "use_cuda": "true"},  "text_to_speech": {"provider": "elevenlabs", "model": "test_model"}}

        tts = ElevenLabsTTS(config)
        audio = MagicMock()
        mock_generate.return_value = audio
        result = tts.generate_voices("mock_script_file")

        self.assertEqual(result, {'Text1': 'mock_filename.mp3'})
        mock_generate.assert_called_once_with(text='Text1',
                                              voice='Rachel',
                                              model='test_model')
        mock_save.assert_called_once_with(audio, "mock_filename.mp3")

    @patch('builtins.open', unittest.mock.mock_open(read_data="Audio:\nTitle:Title1\n🐿️:.cache/sound.wav"))
    @patch('plugins.tts.elevenlabs_tts.is_valid_filename')
    @patch("plugins.tts.elevenlabs_tts.ElevenLabs.generate")
    @patch("plugins.tts.elevenlabs_tts.save")
    def test_generate_voices_not_called(self, mock_save, mock_generate, mock_is_valid_filename):

        config = {"global": {"width": 100, "height": 100,
                             "use_cuda": "true"},  "text_to_speech": {"provider": "elevenlabs", "model": "test_model"}}

        tts = ElevenLabsTTS(config)
        audio = MagicMock()
        mock_generate.return_value = audio
        result = tts.generate_voices("mock_script_file")

        self.assertEqual(result, {'.cache/sound.wav': '.cache/sound.wav'})
        mock_is_valid_filename.assert_called_once_with(".cache/sound.wav")
        mock_generate.assert_not_called()
        mock_save.assert_not_called()

    @patch('builtins.open', unittest.mock.mock_open(read_data="Audio:\nTitle:Title1\n🐿️:Text1\n🐶:Hello\n👨‍🚀:Hi"))
    @patch('plugins.tts.elevenlabs_tts.is_valid_filename', lambda x: False)
    @patch('plugins.tts.elevenlabs_tts.Cache.get_file_path', lambda x, y:  None)
    @patch('plugins.tts.elevenlabs_tts.Cache.store_text', lambda x, y, z:  None)
    @patch('plugins.tts.elevenlabs_tts.create_temp_file', lambda x: "mock_filename.mp3")
    @patch("plugins.tts.elevenlabs_tts.ElevenLabs.generate")
    @patch("plugins.tts.elevenlabs_tts.save")
    def test_if_character_voices_used(self, mock_save, mock_generate):

        config = {"global": {"width": 100, "height": 100,
                             "use_cuda": "true", "characters": [{"name": "🐿️", "voice": "test_voice"},
                                                                {"name": "🐶", "voice": "test_voice2"}]},
                  "text_to_speech": {"provider": "elevenlabs", "model": "test_model"}}

        tts = ElevenLabsTTS(config)
        audio = MagicMock()
        mock_generate.return_value = audio
        result = tts.generate_voices("mock_script_file")

        self.assertEqual(result, {'Text1': 'mock_filename.mp3',
                         'Hello': 'mock_filename.mp3', 'Hi': 'mock_filename.mp3'})

        mock_generate.assert_has_calls([call(text='Text1',
                                             voice='test_voice',
                                             model='test_model'),
                                        call(text='Hello',
                                             voice='test_voice2',
                                             model='test_model'),
                                        call(text='Hi',
                                             voice='Rachel',
                                             model='test_model')])

        self.assertEqual(mock_save.call_count, 3)

        mock_save.assert_has_calls([call(audio, "mock_filename.mp3")])