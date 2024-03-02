from .base_txt2img import BaseTxt2Img
from utils import create_temp_file, is_valid_filename
from diffusers import AutoPipelineForText2Image
import os

class StableDiffusionTxt2Img(BaseTxt2Img):

    USE_CUDA = os.environ['USE_CUDA']

    def __generate_image(self, model, text: str):
        random_filename = create_temp_file(".jpg")
        output_image = model(text, width=self.width, height=self.height, num_inference_steps=1,
                             ignore_mismatched_sizes=True, guidance_scale=0.0).images[0]
        output_image.save(random_filename, format="JPEG")
        return random_filename

    def generate_images(self, script_file: str):
        image_model = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/sd-turbo")
        if self.USE_CUDA == "true":
            image_model.to("cuda")
        image_video_dict = {}
        with open(script_file, 'r') as f:
            for line in f:
                if line.startswith("Image:"):
                    image_text = line.split("Image:")[1].strip()
                    if is_valid_filename(image_text):
                         image_video_dict[image_text] = image_text
                    else:
                        image_file = self.__generate_image(image_model, image_text)
                        image_video_dict[image_text] = image_file
        return image_video_dict
