
from .base_tts import BaseTTS
from utils.helpers import create_temp_file, is_valid_filename
from utils.cache import Cache
from rich.console import Console
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf


class ParlerTTS(BaseTTS):

    _cache = Cache()

    def __init__(self, config):
        super().__init__(config)
        self.__validate()

    def __validate(self):
        console = Console()
        if 'text_to_speech' in self.config:
            tts_config = self.config['text_to_speech']
            if 'model' not in tts_config:
                self.model = 'parler-tts/parler_tts_mini_v0.1'
            elif tts_config['model'] != 'parler-tts/parler_tts_mini_v0.1':
                console.print(
                    "[bold red]Error:[/bold red] 'parler-tts/parler_tts_mini_v0.1' is the only supported 'model' for 'parler' TTS provider.")
                raise ValueError("Invalid 'model' specified in config.")
            else:
                self.model = tts_config['model']
            if 'voice' not in tts_config:
                self.voice = 'A soft female voice.'
            else:
                self.voice = tts_config["voice"]

    def __generate_audio(self, model, tokenizer, text,device,voice):
        random_filename = create_temp_file(".wav")     
        input_ids = tokenizer(voice, return_tensors="pt").input_ids.to(device)
        prompt_input_ids = tokenizer(text, return_tensors="pt").input_ids.to(device)
        generation = model.generate(input_ids=input_ids, prompt_input_ids=prompt_input_ids)
        audio_arr = generation.cpu().numpy().squeeze()
        sf.write(random_filename, audio_arr,samplerate=model.config.sampling_rate, subtype='PCM_24')
        self._cache.store_text(text, random_filename)
        return random_filename

    def generate_voices(self, script_file):
        console = Console()
        device = "cuda:0" if self.use_cuda else "cpu"
        model = None
        tokenzier = None

        emoji_voice_dict = {}
        with open(script_file, 'r') as f:
            for line in f:
                if not line.startswith("Audio:") and not line.startswith("Image:") and not line.startswith("Title:") and ":" in line:
                    voice, _ = self.get_character_data(line)
                    voice_text = line.split(":")[1].strip()
                    if is_valid_filename(voice_text):
                        emoji_voice_dict[voice_text] = voice_text
                    else:
                        existing_file = self._cache.get_file_path(voice_text)
                        if existing_file:
                            emoji_voice_dict[voice_text] = existing_file
                            console.print(f"[green]Loading asset for '{
                                          voice_text}' from cache.")
                            continue

                        if not voice:
                            voice = self.voice
                            
                        if model == None:
                            model = ParlerTTSForConditionalGeneration.from_pretrained("parler-tts/parler_tts_mini_v0.1").to(device)
                            tokenizer = AutoTokenizer.from_pretrained("parler-tts/parler_tts_mini_v0.1")

                        voice_file = self.__generate_audio(model, tokenizer, voice_text,device,voice)
                        emoji_voice_dict[voice_text] = voice_file
        return emoji_voice_dict
