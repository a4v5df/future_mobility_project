from diffusers import StableDiffusionPipeline
import torch
from pathlib import Path

# 전역 파이프라인 캐싱
_pipe = None

def load_pipeline(model_id="runwayml/stable-diffusion-v1-5"):
    global _pipe
    if _pipe is None:
        print("🔄 Stable Diffusion 모델 로드 중...")
        _pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            safety_checker=None  # 필요시 비활성화
        ).to("cpu") # cuda로 바꾸기
        print("✅ 모델 로드 완료")
    return _pipe


# 텍스트 프롬프트를 받아 이미지를 생성하고 저장한 후 경로를 반환합니다.
def generate_image(prompt: str, save_path="output.png") -> str:

    pipe = load_pipeline()
    print(f"🎨 프롬프트로 이미지 생성 중: '{prompt}'")

    image = pipe(prompt).images[0]
    save_path = Path(save_path)
    image.save(save_path)
    print(f"✅ 이미지 저장 완료: {save_path.resolve()}")
    return str(save_path.resolve())
