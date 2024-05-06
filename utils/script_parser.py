from imageio import config
from moviepy.editor import *
#from audio_filters import apply_cartoon_sound_effect
from plugins.tts.espeak_tts import ESpeakTTS
from plugins.tts.bark_tts import BarkTTS
from plugins.txt2img.sdturbo_txt2img import StableDiffusionTxt2Img
from plugins.txt2audio.audio_ldm_txt2audio import AudioLDMTxt2Audio
from plugins.txt2dialog.default_txt2dialog import DefaultTxt2Dialog
from utils.plugin_manager import PluginManager
from rich.console import Console

class ScriptParser:

    @staticmethod
    def parse_script(script_path: str, output_file: str, config_file:str) -> str:
        console = Console()
        
        console.print("[green]Loading config ..")
        plugin_manager = PluginManager(config_file)
        console.print("[green]Loading text to image plugin ...")        
        txt2img = plugin_manager.get_text_to_image_model()
        console.print("[green]Loading text to audio plugin ...") 
        txt2audio = plugin_manager.get_text_to_audio_model()
        console.print("[green]Loading text to dialog plugin ...") 
        txt2dialog = plugin_manager.get_text_to_dialog_model()
        console.print("[green]Loading text to speech plugin ...") 
        tts = plugin_manager.get_text_to_speech_model()

        console.print("[yellow]Converting text to speech ...")
        voices_dict = tts.generate_voices(script_path)
        console.print("[yellow]Converting text to audio ...")
        audio_dict = txt2audio.generate_audio(script_path)
        console.print("[yellow]Converting text to image ...")
        images_dict = txt2img.generate_images(script_path)

        video_clips = []
        actors = []

        fps = 30
        current_image = None
        file_path = script_path
        with console.status("[bold green]Busy...") as status:
            with open(file_path, 'r') as file:
                for line in file:
                    if len(line.strip()) == 0:
                        continue
                    line = line.strip()
                    console.print(f"[yellow]Processing ... {line}")
                    if line.startswith("Title:"):
                        title = line[len("Title:"):].strip()
                        title_duration = 75
                        text_image_path = txt2dialog.create_dialog(
                            current_image, title, type="text")
                        text_clip = ImageClip(
                            text_image_path, duration=title_duration/fps)
                        text_clip = text_clip.set_position('center')
                        video_clips.append(text_clip)
                    elif line.startswith("Image:"):
                        image_path = line[len("Image:"):].strip()
                        img_clip = ImageClip(
                            images_dict[image_path], duration=1/fps)
                        current_image = images_dict[image_path]
                        video_clips.append(img_clip)
                    elif line.startswith("Audio:"):
                        text = line.split(":")[1].strip()
                        audio_file = audio_dict[text]
                        audio_clip = AudioFileClip(audio_file)
                        image_clip = ImageClip(
                            current_image, duration=audio_clip.duration)
                        image_clip = image_clip.set_audio(audio_clip)
                        video_clips.append(image_clip)
                    else:
                        emoji_text = line.split(":")[0].strip()
                        if emoji_text not in actors:
                            actors.append(emoji_text)
                        text = line.split(":")[1].strip()
                        audio_file = voices_dict[text]
                        #TODO: Fix this. Causing audio corruption due to bitrate mismatch.
                        #audio_file = apply_cartoon_sound_effect(
                        #    audio_file, actors.index(emoji_text))
                        audio_clip = AudioFileClip(audio_file)
                        text_image_path = txt2dialog.create_dialog(
                            current_image, emoji_text, type="emoji")
                        emoji_clip = ImageClip(
                            text_image_path, duration=audio_clip.duration)
                        emoji_clip = emoji_clip.set_audio(audio_clip)
                        video_clips.append(emoji_clip)

            final_clip = concatenate_videoclips(video_clips)
            final_clip.write_videofile(output_file, fps=fps,threads=1,verbose=False, logger=None)
            console.print(f"[bold green]Video generated successfully: {output_file}")
        return output_file
