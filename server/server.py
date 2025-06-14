from fastapi import FastAPI
from pydantic import BaseModel
from emotion_state import get_emotion_counter, get_top_emotion, get_latest_emotion_prompt

latest_prompt = None
emotion_triggered = False
text_triggered = False
reset_requested = False
sd_generation_requested = False

app = FastAPI()

class TextInput(BaseModel):
    text: str

@app.get("/status")
def get_status():
    return {
        "emotion_triggered": emotion_triggered,
        "text_triggered": text_triggered,
        "reset_requested": reset_requested,
        "latest_prompt": get_latest_emotion_prompt() or latest_prompt,
        "top_emotion": get_top_emotion(),
        "emotion_counter": get_emotion_counter()
    }

@app.post("/emotion-trigger")
def emotion_trigger():
    global emotion_triggered, text_triggered, sd_generation_requested
    emotion_triggered = True
    text_triggered = False
    sd_generation_requested = True
    return {
        "status": "ok",
        "mode": "emotion",
        "top_emotion": get_top_emotion(),
        "prompt": get_latest_emotion_prompt(),
        "emotion_counter": get_emotion_counter()
    }

@app.post("/text-trigger")
def text_trigger(input: TextInput):
    global latest_prompt, text_triggered, emotion_triggered, sd_generation_requested
    latest_prompt = input.text
    text_triggered = True
    emotion_triggered = False
    sd_generation_requested = True
    return {"status": "ok", "used_prompt": latest_prompt}

@app.post("/reset")
def reset_mode():
    global reset_requested
    reset_requested = True
    return {"status": "ok", "mode": "reset"}

def is_emotion_triggered():
    return emotion_triggered

def is_text_triggered():
    return text_triggered

def get_latest_prompt():
    return latest_prompt

def reset_triggers():
    global emotion_triggered, text_triggered
    emotion_triggered = False
    text_triggered = False

def is_reset_requested():
    return reset_requested

def clear_reset_flag():
    global reset_requested
    reset_requested = False

def is_sd_generation_requested():
    return sd_generation_requested

def clear_sd_generation_flag():
    global sd_generation_requested
    sd_generation_requested = False
