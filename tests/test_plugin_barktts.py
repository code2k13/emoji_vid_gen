
import unittest
from unittest.mock import patch, MagicMock, call
from plugins.tts.bark_tts import BarkTTS


class TestBarkTTS(unittest.TestCase):

    def setUp(self):
        self.config = {"global": {"width": 100, "height": 100,
                                  "use_cuda": "false"},  "text_to_speech": {"model": "suno/bark-small", "voice": "test_voice"}}
        self.tts = BarkTTS(self.config)

    def test_init(self):
        self.assertEqual(self.tts.model, 'suno/bark-small')
        self.assertEqual(self.tts.voice, 'test_voice')

    def test_default_voice(self):
        config = {"global": {"width": 100, "height": 100,
                             "use_cuda": "false"},  "text_to_speech": {"provider": "elevenlabs", "model": "suno/bark-small"}}
        tts = BarkTTS(config)
        self.assertEqual(tts.voice, "v2/en_speaker_6")
        self.assertEqual(tts.model, "suno/bark-small")

    def test_validate(self):
        with patch('rich.console.Console.print') as mock_print:
            config_with_invalid_model = {"global": {"width": 100, "height": 100,
                                                    "use_cuda": "false"}, 'text_to_speech': {"provider": "bark", "model": "invalid"}}

            with self.assertRaises(ValueError):
                BarkTTS(config_with_invalid_model)
            mock_print.assert_called_with(
                "[bold red]Error:[/bold red] 'suno/bark-small' is the only supported 'model' for 'bark' TTS provider.")

    @patch('builtins.open', unittest.mock.mock_open(read_data="Audio:\nTitle:Title1\n🐿️:Text1"))
    @patch('plugins.tts.bark_tts.is_valid_filename', lambda x: False)
    @patch('plugins.tts.bark_tts.Cache.get_file_path', lambda x, y:  None)
    @patch('plugins.tts.bark_tts.Cache.store_text', lambda x, y, z:  None)
    @patch('plugins.tts.bark_tts.create_temp_file', lambda x: "mock_filename.mp3")
    @patch("plugins.tts.bark_tts.AutoProcessor.from_pretrained")
    @patch("plugins.tts.bark_tts.BarkModel.from_pretrained")
    @patch("plugins.tts.bark_tts.sf.write")
    def test_generate_voices(self, mock_sf_write, mock_bark_from_pretrained, mock_auto_prc_from_pretrained):
        config = {"global": {"width": 100, "height": 100, "use_cuda": "false"},
                  "text_to_speech": {"provider": "bark", "model": "suno/bark-small"}}

        tts = BarkTTS(config)

        auto_processor_mock = MagicMock()
        mock_auto_prc_from_pretrained.return_value = auto_processor_mock

        bark_model = MagicMock()
        mock_bark_from_pretrained.return_value = bark_model

        result = tts.generate_voices("mock_script_file")

        self.assertEqual(result, {'Text1': 'mock_filename.mp3'})
        mock_bark_from_pretrained.assert_called_once_with("suno/bark-small")
        mock_auto_prc_from_pretrained.assert_called_once_with(
            "suno/bark-small")
        mock_sf_write.assert_called_once_with("mock_filename.mp3",
                                              bark_model.generate.return_value.cpu().numpy().squeeze(),
                                              samplerate=22050,
                                              subtype='PCM_24')

    @patch('builtins.open', unittest.mock.mock_open(read_data="Audio:\nTitle:Title1\n🐿️:Text1"))
    @patch('plugins.tts.bark_tts.is_valid_filename', lambda x: False)
    @patch('plugins.tts.bark_tts.Cache.get_file_path', lambda x, y:  None)
    @patch('plugins.tts.bark_tts.Cache.store_text', lambda x, y, z:  None)
    @patch('plugins.tts.bark_tts.create_temp_file', lambda x: "mock_filename.mp3")
    @patch("plugins.tts.bark_tts.AutoProcessor.from_pretrained")
    @patch("plugins.tts.bark_tts.BarkModel.from_pretrained")
    @patch("plugins.tts.bark_tts.sf.write")
    def test_generate_voices_cuda(self, mock_sf_write, mock_bark_from_pretrained, mock_auto_prc_from_pretrained):
        config = {"global": {"width": 100, "height": 100, "use_cuda": "true"},
                  "text_to_speech": {"provider": "bark", "model": "suno/bark-small"}}

        tts = BarkTTS(config)

        auto_processor_mock = MagicMock()
        mock_auto_prc_from_pretrained.return_value = auto_processor_mock

        bark_model = MagicMock()
        mock_bark_from_pretrained.return_value = bark_model
        bark_model_to = MagicMock()
        bark_model.to = bark_model_to

        result = tts.generate_voices("mock_script_file")

        self.assertEqual(result, {'Text1': 'mock_filename.mp3'})
        bark_model_to.assert_called_once_with("cuda")
        mock_bark_from_pretrained.assert_called_once_with("suno/bark-small")
        mock_auto_prc_from_pretrained.assert_called_once_with(
            "suno/bark-small")
        mock_sf_write.assert_called_once_with("mock_filename.mp3",
                                              bark_model.generate.return_value.cpu().numpy().squeeze(),
                                              samplerate=22050,
                                              subtype='PCM_24')

    @patch('builtins.open', unittest.mock.mock_open(read_data="Audio:\nTitle:Title1\n🐿️:.cache/sound.wav"))
    @patch('plugins.tts.bark_tts.Cache.get_file_path', lambda x, y:  None)
    @patch('plugins.tts.bark_tts.Cache.store_text', lambda x, y, z:  None)
    @patch('plugins.tts.bark_tts.create_temp_file', lambda x: "mock_filename.mp3")
    @patch('plugins.tts.bark_tts.is_valid_filename')
    @patch("plugins.tts.bark_tts.AutoProcessor.from_pretrained")
    @patch("plugins.tts.bark_tts.BarkModel.from_pretrained")
    @patch("plugins.tts.bark_tts.sf.write")
    def test_generate_voices_not_called(self, mock_sf_write, mock_bark_from_pretrained, mock_auto_prc_from_pretrained, mock_is_valid_filename):

        config = {"global": {"width": 100, "height": 100,
                             "use_cuda": "false"},  "text_to_speech": {"provider": "bark", "model": "suno/bark-small"}}

        tts = BarkTTS(config)

        auto_processor_mock = MagicMock()
        mock_auto_prc_from_pretrained.return_value = auto_processor_mock

        bark_model = MagicMock()
        mock_bark_from_pretrained.return_value = bark_model
        bark_model.to = MagicMock()
        bark_model.generate = MagicMock()

        result = tts.generate_voices("mock_script_file")

        self.assertEqual(result, {'.cache/sound.wav': '.cache/sound.wav'})
        mock_is_valid_filename.assert_called_once_with(".cache/sound.wav")
        bark_model.to.assert_not_called()
        bark_model.generate.assert_not_called()
        auto_processor_mock.assert_not_called()

    @patch('builtins.open', unittest.mock.mock_open(read_data="Audio:\nTitle:Title1\n🐿️:Text1\n🐶:Hello\n👨‍🚀:Hi"))
    @patch('plugins.tts.bark_tts.Cache.get_file_path', lambda x, y:  None)
    @patch('plugins.tts.bark_tts.Cache.store_text', lambda x, y, z:  None)
    @patch('plugins.tts.bark_tts.create_temp_file', lambda x: "mock_filename.mp3")
    @patch('plugins.tts.bark_tts.is_valid_filename', lambda x: False)
    @patch("plugins.tts.bark_tts.AutoProcessor.from_pretrained")
    @patch("plugins.tts.bark_tts.BarkModel.from_pretrained")
    @patch("plugins.tts.bark_tts.sf.write")
    def test_if_character_voices_used(self, mock_sf_write, mock_bark_from_pretrained, mock_auto_prc_from_pretrained):

        config = {"global": {"width": 100, "height": 100,
                             "use_cuda": "false", "characters": [{"name": "🐿️", "voice": "test_voice"},
                                                                 {"name": "🐶", "voice": "test_voice2"}]},
                  "text_to_speech": {"provider": "bark", "model": "suno/bark-small"}}

        tts = BarkTTS(config)

        auto_processor_mock = MagicMock()
        mock_auto_prc_from_pretrained.return_value = auto_processor_mock
        auto_processor_mock.return_value = MagicMock()

        bark_model = MagicMock()
        mock_bark_from_pretrained.return_value = bark_model
        bark_model.to = MagicMock()
        bark_model.generate = MagicMock()
        bark_model.cpu.return_value = MagicMock()

        result = tts.generate_voices("mock_script_file")

        self.assertEqual(result, {'Text1': 'mock_filename.mp3',
                         'Hello': 'mock_filename.mp3', 'Hi': 'mock_filename.mp3'})

        self.assertEqual(auto_processor_mock.call_count, 3)
        auto_processor_mock.assert_has_calls([call('Text1',
                                             voice_preset='test_voice',
                                             return_tensors="pt"),
                                              call('Hello',
                                             voice_preset='test_voice2',
                                              return_tensors="pt"),
                                              call('Hi',
                                             voice_preset='v2/en_speaker_6',
                                             return_tensors="pt")], any_order=True)

        self.assertEqual(mock_sf_write.call_count, 3)

    @patch('builtins.open', unittest.mock.mock_open(read_data="Audio:\nTitle:Title1\n🐿️:Text1\n🐶:Hello\n👨‍🚀:Hi"))
    @patch('plugins.tts.bark_tts.is_valid_filename', lambda x: False)
    @patch('plugins.tts.bark_tts.Cache.get_file_path', lambda x, y:  "abc.mp3")
    @patch('plugins.tts.bark_tts.Cache.store_text', lambda x, y, z:  None)
    @patch('plugins.tts.bark_tts.create_temp_file', lambda x: None)
    @patch("plugins.tts.bark_tts.AutoProcessor.from_pretrained")
    @patch("plugins.tts.bark_tts.BarkModel.from_pretrained")
    @patch("plugins.tts.bark_tts.sf.write")
    def test_if_asset_picked_from_cache(self, mock_sf_write, mock_bark_from_pretrained, mock_auto_prc_from_pretrained):

        config = {"global": {"width": 100, "height": 100,
                             "use_cuda": "true", "characters": [{"name": "🐿️", "voice": "test_voice"},
                                                                {"name": "🐶", "voice": "test_voice2"}]},
                  "text_to_speech": {"provider": "bark", "model": "suno/bark-small"}}

        tts = BarkTTS(config)

        auto_processor_mock = MagicMock()
        mock_auto_prc_from_pretrained.return_value = auto_processor_mock
        auto_processor_mock.return_value = MagicMock()

        bark_model = MagicMock()
        mock_bark_from_pretrained.return_value = bark_model
        bark_model.to = MagicMock()
        bark_model.generate = MagicMock()
        bark_model.cpu.return_value = MagicMock()

        result = tts.generate_voices("mock_script_file")

        self.assertEqual(result, {'Text1': 'abc.mp3',
                         'Hello': 'abc.mp3', 'Hi': 'abc.mp3'})
        self.assertEqual(mock_sf_write.call_count, 0)
        self.assertEqual(auto_processor_mock.call_count,0)
        self.assertEqual(bark_model.generate.call_count,0)


if __name__ == '__main__':
    unittest.main()
