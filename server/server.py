from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import threading

# 전역 상태 공유 변수
latest_prompt = None
emotion_triggered = False
text_triggered = False

app = FastAPI()

class TextInput(BaseModel):
    text: str

@app.post("/emotion-trigger")
def emotion_trigger():
    global emotion_triggered, text_triggered
    emotion_triggered = True
    text_triggered = False
    return {"status": "ok", "mode": "emotion"}

@app.post("/text-trigger")
def text_trigger(input: TextInput):
    global latest_prompt, text_triggered, emotion_triggered
    latest_prompt = input.text
    text_triggered = True
    emotion_triggered = False
    return {"status": "ok", "used_prompt": latest_prompt}