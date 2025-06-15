from diffusers import StableDiffusionPipeline
import torch
from typing import Optional

class SDGenerator:
    def __init__(self, model_name: str = 'runwayml/stable-diffusion-v1-5', device: str = 'cpu'):
        self.pipe = StableDiffusionPipeline.from_pretrained(model_name)
        self.pipe = self.pipe.to(device)

    # def generate_prompt(self, emotion: str, context: Optional[str] = None) -> str:
    #     prompt = f"A scene expressing {emotion}"
    #     if context:
    #         prompt += f", {context}"
    #     return prompt

    def generate_image(self, prompt: str, height: int = 512, width: int = 512):
        with open("prompt_log.txt", "a", encoding="utf-8") as f:
            f.write(prompt + "\n")
            print("🖼️입력된 프롬프트 : ", prompt)
        image = self.pipe(prompt, height=height, width=width).images[0]
        return image
