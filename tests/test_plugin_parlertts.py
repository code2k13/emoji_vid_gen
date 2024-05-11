
import unittest
from unittest.mock import patch, MagicMock, call
from plugins.tts.parler_tts import ParlerTTS


class TestParlerTTS(unittest.TestCase):

    def setUp(self):
        self.config = {"global": {"width": 100, "height": 100,
                                  "use_cuda": "false"},  "text_to_speech": {"model": "parler-tts/parler_tts_mini_v0.1", "voice": "test_voice"}}
        self.tts = ParlerTTS(self.config)

    def test_init(self):
        self.assertEqual(self.tts.model, 'parler-tts/parler_tts_mini_v0.1')
        self.assertEqual(self.tts.voice, 'test_voice')

    def test_default_voice(self):
        config = {"global": {"width": 100, "height": 100,
                             "use_cuda": "false"},  "text_to_speech": {"provider": "parler", "model": "parler-tts/parler_tts_mini_v0.1"}}
        tts = ParlerTTS(config)
        self.assertEqual(tts.model, "parler-tts/parler_tts_mini_v0.1")
        self.assertEqual(tts.voice, "A soft female voice.")

    def test_validate(self):
        with patch('rich.console.Console.print') as mock_print:
            config_with_invalid_model = {"global": {"width": 100, "height": 100,
                                                    "use_cuda": "false"}, 'text_to_speech': {"provider": "parler", "model": "invalid"}}

            with self.assertRaises(ValueError):
                ParlerTTS(config_with_invalid_model)
            mock_print.assert_called_with(
                "[bold red]Error:[/bold red] 'parler-tts/parler_tts_mini_v0.1' is the only supported 'model' for 'parler' TTS provider.")

    def __generate_model_mock(self, mock_parler_from_pretrained):
        mock_chain = MagicMock()
        mock_to = MagicMock()
        mock_generate = MagicMock()
        mock_cpu = MagicMock()
        mock_numpy = MagicMock()
        mock_squeeze = MagicMock()

        mock_chain.to.return_value = mock_to
        mock_to.generate.return_value = mock_generate
        mock_generate.cpu.return_value = mock_cpu
        mock_cpu.numpy.return_value = mock_numpy
        mock_numpy.squeeze.return_value = mock_squeeze
        sample_rate = mock_to.config.sampling_rate
        mock_parler_from_pretrained.return_value = mock_chain
        return mock_squeeze, sample_rate

    @patch('builtins.open', unittest.mock.mock_open(read_data="Audio:\nTitle:Title1\n🐿️:Text1"))
    @patch('plugins.tts.parler_tts.is_valid_filename', lambda x: False)
    @patch('plugins.tts.parler_tts.Cache.get_file_path', lambda x, y:  None)
    @patch('plugins.tts.parler_tts.Cache.store_text', lambda x, y, z:  None)
    @patch('plugins.tts.parler_tts.create_temp_file', lambda x: "mock_filename.mp3")
    @patch("plugins.tts.parler_tts.AutoTokenizer.from_pretrained")
    @patch("plugins.tts.parler_tts.ParlerTTSForConditionalGeneration.from_pretrained")
    @patch("plugins.tts.parler_tts.sf.write")
    def test_generate_voices(self, mock_sf_write, mock_parler_from_pretrained, mock_auto_token_from_pretrained):
        config = {"global": {"width": 100, "height": 100, "use_cuda": "false"},
                  "text_to_speech": {"provider": "parler", "model": "parler-tts/parler_tts_mini_v0.1"}}

        tts = ParlerTTS(config)

        auto_tokenizer_mock = MagicMock()
        mock_auto_token_from_pretrained.return_value = auto_tokenizer_mock
        output, sample_rate = self.__generate_model_mock(
            mock_parler_from_pretrained)
        result = tts.generate_voices("mock_script_file")

        self.assertEqual(result, {'Text1': 'mock_filename.mp3'})
        mock_parler_from_pretrained.assert_called_once_with(
            "parler-tts/parler_tts_mini_v0.1")
        mock_auto_token_from_pretrained.assert_called_once_with(
            "parler-tts/parler_tts_mini_v0.1")
        mock_sf_write.assert_called_once_with("mock_filename.mp3",
                                              output,
                                              samplerate=sample_rate,
                                              subtype='PCM_24')

    @patch('builtins.open', unittest.mock.mock_open(read_data="Audio:\nTitle:Title1\n🐿️:Text1"))
    @patch('plugins.tts.parler_tts.is_valid_filename', lambda x: False)
    @patch('plugins.tts.parler_tts.Cache.get_file_path', lambda x, y:  None)
    @patch('plugins.tts.parler_tts.Cache.store_text', lambda x, y, z:  None)
    @patch('plugins.tts.parler_tts.create_temp_file', lambda x: "mock_filename.mp3")
    @patch("plugins.tts.parler_tts.AutoTokenizer.from_pretrained")
    @patch("plugins.tts.parler_tts.ParlerTTSForConditionalGeneration.from_pretrained")
    @patch("plugins.tts.parler_tts.sf.write")
    def test_generate_voices_cuda(self, mock_sf_write, mock_parler_from_pretrained, mock_auto_token_from_pretrained):
        config = {"global": {"width": 100, "height": 100, "use_cuda": "true"},
                  "text_to_speech": {"provider": "parler", "model": "parler-tts/parler_tts_mini_v0.1"}}

        tts = ParlerTTS(config)

        auto_tokenizer_mock = MagicMock()
        mock_auto_token_from_pretrained.return_value = auto_tokenizer_mock
        output, sample_rate = self.__generate_model_mock(
            mock_parler_from_pretrained)
        result = tts.generate_voices("mock_script_file")

        self.assertEqual(result, {'Text1': 'mock_filename.mp3'})
        mock_parler_from_pretrained.return_value.to.assert_called_once_with(
            "cuda:0")
        mock_parler_from_pretrained.assert_called_once_with(
            "parler-tts/parler_tts_mini_v0.1")
        mock_auto_token_from_pretrained.assert_called_once_with(
            "parler-tts/parler_tts_mini_v0.1")
        mock_sf_write.assert_called_once_with("mock_filename.mp3",
                                              output,
                                              samplerate=sample_rate,
                                              subtype='PCM_24')

    @patch('builtins.open', unittest.mock.mock_open(read_data="Audio:\nTitle:Title1\n🐿️:.cache/sound.wav"))
    @patch('plugins.tts.parler_tts.Cache.get_file_path', lambda x, y:  None)
    @patch('plugins.tts.parler_tts.Cache.store_text', lambda x, y, z:  None)
    @patch('plugins.tts.parler_tts.create_temp_file', lambda x: "mock_filename.mp3")
    @patch('plugins.tts.parler_tts.is_valid_filename')
    @patch("plugins.tts.parler_tts.AutoTokenizer.from_pretrained")
    @patch("plugins.tts.parler_tts.ParlerTTSForConditionalGeneration.from_pretrained")
    @patch("plugins.tts.parler_tts.sf.write")
    def test_generate_voices_not_called(self, mock_sf_write, mock_parler_from_pretrained, mock_auto_token_from_pretrained, mock_is_valid_filename):

        config = {"global": {"width": 100, "height": 100,
                             "use_cuda": "false"},  "text_to_speech": {"provider": "parler", "model": "parler-tts/parler_tts_mini_v0.1"}}

        tts = ParlerTTS(config)

        auto_tokenizer_mock = MagicMock()
        mock_auto_token_from_pretrained.return_value = auto_tokenizer_mock
        _ = self.__generate_model_mock(mock_parler_from_pretrained)
        result = tts.generate_voices("mock_script_file")

        self.assertEqual(result, {'.cache/sound.wav': '.cache/sound.wav'})
        mock_is_valid_filename.assert_called_once_with(".cache/sound.wav")
        mock_auto_token_from_pretrained.return_value.to.assert_not_called()
        mock_auto_token_from_pretrained.return_value.generate.assert_not_called()
        mock_auto_token_from_pretrained.assert_not_called()

    @patch('builtins.open', unittest.mock.mock_open(read_data="Audio:\nTitle:Title1\n🐿️:Text1\n🐶:Hello\n👨‍🚀:Hi"))
    @patch('plugins.tts.parler_tts.Cache.get_file_path', lambda x, y:  None)
    @patch('plugins.tts.parler_tts.Cache.store_text', lambda x, y, z:  None)
    @patch('plugins.tts.parler_tts.create_temp_file', lambda x: "mock_filename.mp3")
    @patch('plugins.tts.parler_tts.is_valid_filename', lambda x: False)
    @patch("plugins.tts.parler_tts.AutoTokenizer.from_pretrained")
    @patch("plugins.tts.parler_tts.ParlerTTSForConditionalGeneration.from_pretrained")
    @patch("plugins.tts.parler_tts.sf.write")
    def test_if_character_voices_used(self, mock_sf_write, mock_parler_from_pretrained, mock_auto_token_from_pretrained):

        config = {"global": {"width": 100, "height": 100,
                             "use_cuda": "false", "characters": [{"name": "🐿️", "voice": "test_voice"},
                                                                 {"name": "🐶", "voice": "test_voice2"}]},
                  "text_to_speech": {"provider": "parler", "model": "parler-tts/parler_tts_mini_v0.1"}}

        tts = ParlerTTS(config)

        auto_tokenizer_mock = MagicMock()
        mock_auto_token_from_pretrained.return_value = auto_tokenizer_mock

        mock_squeeze,_ = self.__generate_model_mock(mock_parler_from_pretrained)
        result = tts.generate_voices("mock_script_file")

        self.assertEqual(result, {'Text1': 'mock_filename.mp3',
                         'Hello': 'mock_filename.mp3', 'Hi': 'mock_filename.mp3'})

        mock_squeeze.assert_has_calls([call('test_voice',
                                                   return_tensors="pt"),
                                              call('Text1',
                                                   return_tensors="pt"),
                                              call('test_voice2',
                                                   return_tensors="pt"),
                                              call('Hello',
                                                   return_tensors="pt"),
                                              call('A soft female voice.',
                                                   return_tensors="pt"),
                                              call('Hi',
                                                   return_tensors="pt"),], any_order=True)

        generate_method = mock_parler_from_pretrained.return_value.to().generate
        self.assertEqual(generate_method.call_count,3)
        self.assertEqual(mock_sf_write.call_count, 3)

    @patch('builtins.open', unittest.mock.mock_open(read_data="Audio:\nTitle:Title1\n🐿️:Text1\n🐶:Hello\n👨‍🚀:Hi"))
    @patch('plugins.tts.parler_tts.is_valid_filename', lambda x: False)
    @patch('plugins.tts.parler_tts.Cache.get_file_path', lambda x, y:  "abc.mp3")
    @patch('plugins.tts.parler_tts.Cache.store_text', lambda x, y, z:  None)
    @patch('plugins.tts.parler_tts.create_temp_file', lambda x: None)
    @patch("plugins.tts.parler_tts.AutoTokenizer.from_pretrained")
    @patch("plugins.tts.parler_tts.ParlerTTSForConditionalGeneration.from_pretrained")
    @patch("plugins.tts.parler_tts.sf.write")
    def test_if_asset_picked_from_cache(self, mock_sf_write,  mock_parler_from_pretrained, mock_auto_token_from_pretrained):

        config = {"global": {"width": 100, "height": 100,
                             "use_cuda": "true", "characters": [{"name": "🐿️", "voice": "test_voice"},
                                                                {"name": "🐶", "voice": "test_voice2"}]},
                  "text_to_speech": {"provider": "parler", "model": "parler-tts/parler_tts_mini_v0.1"}}

        tts = ParlerTTS(config)

        auto_tokenizer_mock = MagicMock()
        mock_auto_token_from_pretrained.return_value = auto_tokenizer_mock

        mock_squeeze,_ = self.__generate_model_mock(mock_parler_from_pretrained)
        result = tts.generate_voices("mock_script_file")
        generate_method = mock_parler_from_pretrained.return_value.to().generate

        self.assertEqual(result, {'Text1': 'abc.mp3',
                         'Hello': 'abc.mp3', 'Hi': 'abc.mp3'})
        self.assertEqual(mock_sf_write.call_count, 0)
        self.assertEqual(mock_squeeze.call_count,0)
        self.assertEqual(generate_method.generate.call_count,0)


if __name__ == '__main__':
    unittest.main()
