from utils.helpers import create_temp_file
from pydub import AudioSegment

def apply_cartoon_sound_effect(input_file_path,semitones =0) -> str:
    random_filename = create_temp_file(".wav")
    semitones = (semitones+1)*2
    audio = AudioSegment.from_file(input_file_path)
    shifted_audio = audio._spawn(audio.raw_data, overrides={
        "frame_rate": int(audio.frame_rate  * (2 ** (semitones / 12.0)))
    })
    shifted_audio.export(random_filename, format="wav")
    return random_filename