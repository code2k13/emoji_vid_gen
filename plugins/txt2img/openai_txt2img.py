from .base_txt2img import BaseTxt2Img
from utils.helpers import create_temp_file, is_valid_filename 
import requests
from utils.cache import Cache
from rich.console import Console
from PIL import Image
from io import BytesIO
from openai import OpenAI
import time

class OpenAI_Txt2Img(BaseTxt2Img):

    _cache =Cache()

    def __init__(self, config):
        super().__init__(config)
        self.__validate()

    def __validate(self):
        console = Console()
        if 'text_to_image' in self.config:
            text_to_img_config = self.config['text_to_image']
            default_model = "dall-e-3"
            if 'model' not in text_to_img_config:
                self.model = default_model
                console.print("[grey]Model not specified for text_to_image, defaulting to {default_model} ")
            elif text_to_img_config['model'] not in [default_model,"dall-e-2"]:
                console.print(
                    "[bold red]Error:[/bold red] 'dall-e-3' and 'dall-e-2' are the only supported 'models' for 'openai' provider.")
                raise ValueError("Invalid 'model' specified in config.")
            else:
                self.model = text_to_img_config['model']

            if 'quality'  in text_to_img_config:
                self.quality = text_to_img_config["quality"]
            else:
                self.quality = "standard"

            if 'request_delay_sec' in text_to_img_config:
                self.request_delay_sec = int(text_to_img_config['request_delay_sec'])
            else:
                console.print("[grey] Using default delay of 12 seconds for openai txt2img requests")
                self.request_delay_sec = 12


    def __generate_image(self, text: str):
        random_filename = create_temp_file(".jpg")
        
        client = OpenAI()
        response = client.images.generate(
            model=self.model,
            prompt=text,
            size=f"{self.width}x{self.height}",
            quality=self.quality,
            n=1,
        )

        image_url = response.data[0].url
        image_response = requests.get(image_url)
        image_data = Image.open(BytesIO(image_response.content))
        image_data.save(random_filename,format="JPEG")

        self._cache.store_text(text,random_filename)
        return random_filename

    def generate_images(self, script_file: str):  
        console = Console()    
        image_video_dict = {}
        with open(script_file, 'r') as f:
            for line in f:
                if line.startswith("Image:"):
                    image_text = line.split("Image:")[1].strip()
                    if is_valid_filename(image_text):
                        image_video_dict[image_text] = image_text
                    else:
                        existing_file = self._cache.get_file_path(image_text)
                        if existing_file:
                            image_video_dict[image_text] = existing_file
                            console.print(f"[green]Loading asset for '{image_text}' from cache.")
                            continue
                        image_file = self.__generate_image(image_text)
                        time.sleep(self.request_delay_sec)
                        image_video_dict[image_text] = image_file
        return image_video_dict
