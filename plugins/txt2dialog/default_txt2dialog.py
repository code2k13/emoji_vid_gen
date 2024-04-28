
from .base_txt2dialog import BaseText2Dialog
from utils.helpers import create_temp_file, is_valid_filename
from typing import Literal
import random
from PIL import Image, ImageDraw, ImageFont
import os
from utils.cache import Cache
import unicodedata

class DefaultTxt2Dialog(BaseText2Dialog):
    _cache = Cache()
    _font_size= 109

    def create_dialog(self, image_path, text: str, type: Literal["text", "emoji"] = "text") -> str:

        # 🎙️ is reserved for narrator. Dont draw emoji
        if type=="emoji" and text == "🎙️":
            return image_path

        text = text.strip()
        if is_valid_filename(text) and type == "text":
            return text

        random_filename = create_temp_file(".png")
        background_image = Image.open(image_path)
        image = Image.new("RGBA", background_image.size, (0, 0, 0, 0))
        image = image.convert('RGBA')
        draw = ImageDraw.Draw(image)

        if type == "emoji":
            font = ImageFont.truetype("NotoColorEmoji.ttf", size=self._font_size)
            x = (self.width)//2 - self._font_size//2
            y = self.height - self._font_size - 30
            seed_image_path = self._cache.get_file_path(
                unicodedata.name(text[0]))
            if seed_image_path:
                seeded_character_image = Image.open(seed_image_path)
                seeded_character_image = seeded_character_image.resize(
                    (self._font_size, self._font_size))
                image.paste(seeded_character_image, (x, y),
                            mask=seeded_character_image)
            else:
                #center = (x+self._font_size-40, y+60)
                #radius = 100
                #color = (0, 0, 0, 128)
                #draw.ellipse((center[0] - radius, center[1] - radius,
                #              center[0] + radius, center[1] + radius), fill=color)
                draw.text((x, y), text, fill=(0, 0, 0),
                          font=font, embedded_color=True)

            val = random.choice(["🗨️", "💬"])
            if val == "💬":
                draw.text((x+self._font_size, y-self._font_size), val, fill=(0, 0, 0),
                          font=font, embedded_color=True)
            else:
                draw.text((x-self._font_size, y-self._font_size), val, fill=(0, 0, 0),
                          font=font, embedded_color=True)
        else:
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            if os.path.exists(font_path) and os.access(font_path, os.R_OK):
                font = ImageFont.truetype(font_path, size=60)
            else:
                font = ImageFont.load_default()
            y = (self.height) // 2
            text_width = draw.textlength(text, font=font)
            x = (self.width - text_width)//2
            draw.text((x, y), text, fill=(0, 0, 0), font=font)
            draw.text((x+2, y+2), text, fill=(255, 255, 255), font=font)

        background_image.paste(image, (0, 0), mask=image)
        background_image.save(random_filename, 'PNG')
        return random_filename
