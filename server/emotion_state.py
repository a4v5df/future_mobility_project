from collections import Counter
from generators.sd_generator import SDGenerator
from chatgpt_prompt import generate_sd_prompt  

emotion_counter = Counter()
latest_emotion_prompt = None
latest_text_prompt = None


HARDCODED_PROMPTS = {
    "happy": (
        "Golden sunlight filtering through trees in a lively park, children laughing, blooming flowers, vibrant atmosphere, warm and cheerful mood"
    ),
    "sad": (
        "A rainy street with soft reflections, gray overcast sky, a person holding an umbrella alone, melancholic and introspective tone"
    ),
    "angry": (
        "A dramatic thunderstorm over a dark urban skyline, intense lightning in the sky, heavy shadows, chaotic and aggressive atmosphere"
    ),
    "surprise": (
        "Colorful fireworks exploding over a calm lake at night, reflections on water, silhouettes of people watching in awe, magical and unexpected"
    ),
    "neutral": (
        "A tranquil forest at dawn with mist rising between trees, soft sunlight breaking through leaves, peaceful and balanced mood"
    )
}

def update_emotion_counter(emotions):
    for e in emotions:
        emotion_counter[e.label] += 1

def get_emotion_counter():
    return dict(emotion_counter)

def get_top_emotion():
    if emotion_counter:
        return emotion_counter.most_common(1)[0][0]
    return "neutral"    # 기본은 neutral

def generate_prompt_from_top_emotion():
    global latest_emotion_prompt
    top = get_top_emotion()
    # prompt = SDGenerator().generate_prompt(top)
    prompt = HARDCODED_PROMPTS.get(top, "A neutral scene with natural elements")
    latest_emotion_prompt = prompt
    return prompt

def generate_prompt_from_text_input(user_input: str):
    global latest_text_prompt
    prompt = generate_sd_prompt(user_input)
    latest_text_prompt = prompt
    return prompt

def get_latest_emotion_prompt():
    return latest_emotion_prompt

def clear_emotions():
    emotion_counter.clear()
    global latest_emotion_prompt, latest_text_prompt
    latest_emotion_prompt = None
    latest_text_prompt = None