from collections import Counter
from generators.sd_generator import SDGenerator

emotion_counter = Counter()
latest_emotion_prompt = None

def update_emotion_counter(emotions):
    for e in emotions:
        emotion_counter[e.label] += 1

def get_emotion_counter():
    return dict(emotion_counter)

def get_top_emotion():
    if emotion_counter:
        return emotion_counter.most_common(1)[0][0]
    return "neutral"

def generate_prompt_from_top_emotion():
    global latest_emotion_prompt
    top = get_top_emotion()
    prompt = SDGenerator().generate_prompt(top)
    latest_emotion_prompt = prompt
    return prompt

def get_latest_emotion_prompt():
    return latest_emotion_prompt

def clear_emotions():
    emotion_counter.clear()
    global latest_emotion_prompt
    latest_emotion_prompt = None