# Emoji Video Generator

![sample script converted to video](docs/emoji_vid_generator.gif)

The objective of `EmojiVidGen` is to develop a straightforward system capable of converting a basic script stored in a text file into a video. The aim is to ensure simplicity to the extent that even individuals with a bit of creativity and typing skills could produce a movie effortlessly. This tool is designed to operate smoothly on a computer with 8 GB of memory, offering reasonable processing speeds even without GPUs. While initially intended for entertainment with GenAI, I believe that, in capable hands, it holds the potential to generate pretty cool content. This project is experimental in nature, crafted primarily for educational purposes

> This software is intended solely for educational purposes. It is used at your own discretion and risk. Please be aware that the AI models utilized in this code may have restrictions against commercial usage.

## Installation


```bash
sudo apt update
sudo apt install espeak ffmpeg

```

```bash
git clone https://github.com/code2k13/emoji_vid_gen
cd emoji_vid_gen
wget https://github.com/googlefonts/noto-emoji/raw/main/fonts/NotoColorEmoji.ttf
```


```bash
pip install -r requirements.txt
```

## Sample script

> Note: A script should always start with a `Image:` directive

```bash
Image: Cartoon illustration showing a beautiful landscape with mountains and a road.
Audio: Tranquil calm music occasional chirping of birds.
Title: EmojiVidGen
🐼: Emoji vid gen is a tool to create videos from text files using AI.
```


## How to run

```bash
python generate_video.py scripts/hello.txt hello.mp4
```

## A full featured example

```bash
Image:  A single trophy kept on table. comic book style.
Audio: Upbeat introduction music for cartoon show.
Title: Emoji Quiz Showdown
🎤: "Welcome to the Emoji Quiz Showdown! Are you ready to test your knowledge?"
🐱: "Meow! I'm ready!"
🐶: "Woof! Let's do this!"
Image: Cartoon illustration of the Eiffel Tower.
🎤: "First question What is the capital of France?"
Audio: suspenseful music playing.
🐱: "Paris!"
Audio: people applauding sound
Image: Cartoon illustration of Mount Everest.
🎤: "Correct! One point for the cat! Next question  What is the tallest mountain in the world?"
Audio: suspenseful music playing.
🐶: "Mount Everest!"
Audio: people applauding sound
Image: Cartoon illustration of a water molecule.
🎤: "Right again! One point for the dog! Next question  What is the chemical symbol for water?"
Audio: suspenseful music playing.
🐱: "H2O!"
Audio: people applauding sound
Image: Cartoon illustration of a globe with seven continents.
🎤: "Correct! Another point for the cat! Last question How many continents are there on Earth?"
Audio: suspenseful music playing.
🐶: "Seven!"
Audio: people applauding sound
🎤: "Correct! It's a tie! You both did great! Thanks for playing the Emoji Quiz Showdown!"
```

## The Narrator
The emoji `🎙️` is reserved as narrator. Using it at start of line will cause the system to only generated sound and not output any image on background.

## Seeding character images
Sometimes you may not want to use emojis as characters in your video. In such cases you can use `seed_character.py` tool as follows

```bash
python3 seed_character.py add 🐿️  --filename squirrel.png 
```

The above commands instructs the video generation script to use `squirrel.png` every time the 🐿️ emojis is encountered. It is also possible to remove the character seeding by using:

```bash
python3 seed_character.py remove 🐿️
```
When seeding characters ensure that you use square images, background is removed from images and they are stored as PNG.

## Using presets

If you've followed the earlier instructions for video generation, you might have noticed that the default setup uses `espeak` as the text-to-speech engine, resulting in a robotic-sounding output. EmojiVidGen is built with an internal structure comprising plugins, each capable of modifying how a task is executed or which model is used.

For instance, you can designate a specific plugin for each type of generation task—be it text-to-image, text-to-audio, or text-to-speech. Because each plugin operates with its unique model and method, configuring these settings individually can be overwhelming. To simplify this process, I've introduced the concept of presets. You can apply a preset by supplying the `--preset` option to the `generate_video.py` file.

For example the below preset uses a profile called `local_medium`.
```bash
python generate_video.py scripts/hello.txt hello.mp4 --preset local_medium
```

All profiles are stored in `./profiles folder`. To create a new profile (say `custom_profile`), just create a new `custom_profile.yaml` file in `./profiles' folder and start using it like this

```bash
python generate_video.py scripts/hello.txt hello.mp4 --preset custom_profile
```

## Available Presets

| Preset Name | Description |
|-----------------|-----------------|
| local_basic   | Uses Huggingface's Stable Diffusion pipeline with `stabilityai/sd-turbo` model for text to image. Uses `espeak` for text to speech and Huggingface's AudioLDM pipeline for text to audio.   |
| local_basic_gpu    | Same as local_basic, but with cuda support enabled.   |
| local_medium    | Similar to local_basic but uses `brave` as text to speech engine and `stabilityai/sdxl-turbo` model for text to image   |
| local_medium    | Same as local_medium, but with cuda support is enabled.   |
| eleven_medium    | Same as local_medium, but uses `ElevenLabs` text to speech API support is enabled. Needs internet and `ELEVEN_API_KEY` variable to be defined in `.env` file. Needs internet and ElevenLabs account.   |


## Creating custom presets

WIP

## Using pre-created assets

Ensure that asset files are present in `.cache` folder. Create the script in this manner

```bash
Image: .cache/existing_background_hd.png
Audio: Funny opening music jingle.
Title: EmojiVidGen
🐼: .cache/existing_speech.wav
```

## Change default width and height of image

Copy a suitable profile and modify following lines:

```yaml
global:
  width: 1152
  height: 896
```

Note: This setting does affect the output of stable diffusion. Not all resolutions work that well. For  more information checkout this
 https://replicate.com/guides/stable-diffusion/how-to-use/ . Stable Diffusion seems to work well with square aspect ratios.


## Known issues

You will see this error message when using `espeak` text to speech provider. 

```bash
Traceback (most recent call last):
  File "/usr/local/lib/python3.10/dist-packages/pyttsx3/drivers/espeak.py", line 171, in _onSynth
    self._proxy.notify('finished-utterance', completed=True)
ReferenceError: weakly-referenced object no longer exists
```

Ignore this error for now as it does not affect the output.


If you receive the below error, delete the `.cache` directory

```bash
  File "plyvel/_plyvel.pyx", line 247, in plyvel._plyvel.DB.__init__
  File "plyvel/_plyvel.pyx", line 88, in plyvel._plyvel.raise_for_status
plyvel._plyvel.IOError: b'IO error: lock .cache/asset/LOCK: Resource temporarily unavailable'
```