from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from diffusion.generate import generate_image
from camera.show_overlay import show_image_overlay  

import threading

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SpeechInput(BaseModel):
    text: str

@app.post("/generate")
async def generate(speech: SpeechInput):
    prompt = speech.text
    print(f"🗣️ 사용자 프롬프트 수신: {prompt}")

    def run_generation():
        image_path = generate_image(prompt)
        show_image_overlay(image_path)  # 생성된 이미지를 실시간 영상에 오버레이

    threading.Thread(target=run_generation).start()

    return {"status": "accepted", "message": f"프롬프트 수신 완료: {prompt}"}
