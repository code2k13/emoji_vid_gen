from .base_txt2img import BaseTxt2Img
from utils.helpers import create_temp_file, is_valid_filename
from diffusers import AutoPipelineForText2Image
import os
from utils.cache import Cache
from rich.console import Console

class StableDiffusionTxt2Img(BaseTxt2Img):

    _cache =Cache()

    def __init__(self, config):
        super().__init__(config)
        self.__validate()

    def __validate(self):
        console = Console()
        if 'text_to_image' in self.config:
            text_to_img_config = self.config['text_to_image']
            default_model = "stabilityai/sd-turbo"
            if 'model' not in text_to_img_config:
                self.model = default_model
                console.print("[grey]Model not specified for text_to_image, defaulting to {default_model} ")
            elif text_to_img_config['model'] not in [default_model,"stabilityai/sdxl-turbo"]:
                console.print(
                    "[bold red]Error:[/bold red] 'stabilityai/sd-turbo' and 'stabilityai/sdxl-turbo' are the only supported 'models' for 'hf_text2image' provider.")
                raise ValueError("Invalid 'model' specified in config.")
            else:
                self.model = text_to_img_config['model']

    def __generate_image(self, model, text: str):
        random_filename = create_temp_file(".jpg")
        output_image = model(text, width=self.width, height=self.height, num_inference_steps=1,
                             ignore_mismatched_sizes=True, guidance_scale=0.0).images[0]
        output_image.save(random_filename, format="JPEG")
        self._cache.store_text(text,random_filename)
        return random_filename

    def generate_images(self, script_file: str):  
        console = Console()
        model_name  = self.model
        image_model = None       
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
                        if not image_model:
                            image_model = AutoPipelineForText2Image.from_pretrained(model_name)
                            if self.use_cuda:
                                image_model.to("cuda")
                        image_file = self.__generate_image(
                            image_model, image_text)
                        image_video_dict[image_text] = image_file
        return image_video_dict
