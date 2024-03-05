from moviepy.editor import *
#from audio_filters import apply_cartoon_sound_effect
from plugins.tts.espeak_tts import ESpeakTTS
from plugins.tts.bark_tts import BarkTTS
from plugins.txt2img.sdturbo_txt2img import StableDiffusionTxt2Img
from plugins.txt2audio.audio_ldm_txt2audio import AudioLDMTxt2Audio
from plugins.txt2dialog.default_txt2dialog import DefaultTxt2Dialog


class ScriptParser:

    @staticmethod
    def parse_script(script_path: str, output_file: str) -> str:
        if os.getenv("VIDEO_WIDTH") is not None:
            width = int(os.getenv("VIDEO_WIDTH"))
        else:
            width = 768

        if os.getenv("VIDEO_HEIGHT") is not None:
            height = int(os.getenv("VIDEO_HEIGHT"))
        else:
            height = 768

        if os.getenv("TTS_HIGH_QUALITY") == "true":
            tts = BarkTTS()
        else:
            tts = ESpeakTTS()
        txt2img = StableDiffusionTxt2Img(width, height)
        txt2audio = AudioLDMTxt2Audio()
        txt2dialog = DefaultTxt2Dialog(width, height)

        voices_dict = tts.generate_voices(script_path)
        audio_dict = txt2audio.generate_audio(script_path)
        images_dict = txt2img.generate_images(script_path)

        video_clips = []
        actors = []

        fps = 30
        current_image = None
        file_path = script_path

        with open(file_path, 'r') as file:
            for line in file:
                if len(line.strip()) == 0:
                    continue
                line = line.strip()
                print("Processing ...", line)
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
        final_clip.write_videofile(output_file, fps=fps,threads=1)
        print(f"Video generated successfully: {output_file}")
        return output_file
