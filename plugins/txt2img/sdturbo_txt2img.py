from .base_txt2img import BaseTxt2Img
from utils import create_temp_file, is_valid_filename
from diffusers import AutoPipelineForText2Image
import os
from cache import Cache

class StableDiffusionTxt2Img(BaseTxt2Img):

    USE_CUDA = os.getenv('USE_CUDA')
    USE_SD_TURBO_XL = os.getenv('USE_SD_TURBO_XL')
    _cache =Cache()

    def __generate_image(self, model, text: str):
        random_filename = create_temp_file(".jpg")
        output_image = model(text, width=self.width, height=self.height, num_inference_steps=1,
                             ignore_mismatched_sizes=True, guidance_scale=0.0).images[0]
        output_image.save(random_filename, format="JPEG")
        self._cache.store_text(text,random_filename)
        return random_filename

    def generate_images(self, script_file: str):
   
        if self.USE_SD_TURBO_XL == "true":
            model_name = "stabilityai/sdxl-turbo"
        else:
            model_name = "stabilityai/sd-turbo"
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
                            print(f"Loading asset for '{image_text}' from cache.")
                            continue
                        if not image_model:
                            image_model = AutoPipelineForText2Image.from_pretrained(model_name)
                            if self.USE_CUDA == "true":
                                image_model.to("cuda")
                        image_file = self.__generate_image(
                            image_model, image_text)
                        image_video_dict[image_text] = image_file
        return image_video_dict
