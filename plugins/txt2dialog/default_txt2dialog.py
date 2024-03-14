
from .base_txt2dialog import BaseText2Dialog
from utils import create_temp_file, is_valid_filename
from typing import Literal
import random
from PIL import Image, ImageDraw, ImageFont
import os


class DefaultTxt2Dialog(BaseText2Dialog):

    def create_dialog(self, image_path, text: str, type: Literal["text", "emoji"] = "text") -> str:
        text = text.strip()
        if is_valid_filename(text) and type == "text":
            return text

        random_filename = create_temp_file(".png")
        background_image = Image.open(image_path)
        image = Image.new("RGBA", background_image.size, (0, 0, 0, 0))
        image = image.convert('RGBA')
        draw = ImageDraw.Draw(image)
        y = (self.height) // 2
        if type == "emoji":
            font = ImageFont.truetype("NotoColorEmoji.ttf", size=109)
            y = self.height - 200
        else:
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            if os.path.exists(font_path) and os.access(font_path, os.R_OK):
                font = ImageFont.truetype(font_path, size=60)
            else:
                font = ImageFont.load_default()
        text_width = draw.textlength(text, font=font)
        x = (self.width - text_width)//2

        if type == "emoji":
            center = (x+109-40, y+60)
            radius = 80
            color = (0, 0, 0, 128)
            draw.ellipse((center[0] - radius, center[1] - radius,
                         center[0] + radius, center[1] + radius), fill=color)

        draw.text((x, y), text, fill=(0, 0, 0), font=font, embedded_color=True)
        if type != "emoji":
            draw.text((x+2, y+2), text, fill=(255, 255, 255), font=font)
        else:
            val = random.choice(["🗨️", "💬"])
            if val == "💬":
                draw.text((x+109, y-109), val, fill=(0, 0, 0),
                          font=font, embedded_color=True)
            else:
                draw.text((x-109, y-109), val, fill=(0, 0, 0),
                          font=font, embedded_color=True)

        background_image.paste(image, (0, 0), mask=image)
        background_image.save(random_filename, 'PNG')
        return random_filename
