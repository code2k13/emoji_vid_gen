
import unittest
from unittest.mock import patch, MagicMock
from plugins.tts.bark_tts import BarkTTS


class TestBarkTTS(unittest.TestCase):

    def setUp(self):
        self.config = {"global": {"width": 100, "height": 100,
                                  "use_cuda": "true"},  "text_to_speech": {"model": "suno/bark-small"}}
        self.tts = BarkTTS(self.config)

    def test_init(self):
        self.assertEqual(self.tts.model, 'suno/bark-small')
        self.assertEqual(self.tts.voice, 'v2/en_speaker_6')

    def test_validate(self):
        with patch('rich.console.Console.print') as mock_print:
            config_with_invalid_model = {"global": {"width": 100, "height": 100,
                                                    "use_cuda": "true"}, 'text_to_speech': {"provider": "bark", "model": "invalid"}}

            with self.assertRaises(ValueError):
                BarkTTS(config_with_invalid_model)
            mock_print.assert_called_with(
                "[bold red]Error:[/bold red] 'suno/bark-small' is the only supported 'model' for 'bark' TTS provider.")

if __name__ == '__main__':
    unittest.main()
