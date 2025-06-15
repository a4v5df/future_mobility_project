import openai
import os

api_key = ""

client = openai.OpenAI(api_key = api_key)

def generate_sd_prompt(user_input: str) -> str:
    system_msg = (
        "You are a prompt generator for Stable Diffusion. "
        "Your job is to understand the user's emotional or contextual request and convert it into a vivid, descriptive image prompt. "
        "If the user expresses a mood, feeling, or state of mind, respond with imagery that emotionally matches or provides relief to that state. "
        "Focus on concrete visual elements such as mood, color, setting, and artistic style that match the user's emotional context. "
        "Do not use full sentences or include commands like 'create' or 'generate'. "
        "Return only one concise English prompt suitable for image generation."
    )

    user_msg = f"User input: \"{user_input}\". Generate a detailed prompt for a Stable Diffusion image."

    response = client.chat.completions.create(
        model="gpt-4o",  
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        temperature=0.7,
        max_tokens=150
    )

    return response.choices[0].message.content.strip()  
