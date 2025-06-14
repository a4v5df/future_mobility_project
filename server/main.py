import cv2
import numpy as np
import threading
from camera.capture import Camera
from detectors.obj_detector import ObjectDetector
from detectors.emo_detector import EmotionDetector
from visualizers.overlay import Overlay
from generators.sd_generator import SDGenerator
import uvicorn
import time
from emotion_state import update_emotion_counter, generate_prompt_from_top_emotion, clear_emotions
from server import (
    is_emotion_triggered,
    is_text_triggered,
    get_latest_prompt,
    reset_triggers,
    is_reset_requested,
    clear_reset_flag,
    is_sd_generation_requested,
    clear_sd_generation_flag,
)

sd_img_ready = False
latest_sd_img = None
sd_lock = threading.Lock()
yolo_enabled = False
obj_boxes = []
device = 'cpu'
def generate_sd_background(prompt, height, width, filename):
    global latest_sd_img, sd_img_ready
    sd = SDGenerator(device = device)
    img = sd.generate_image(prompt, height=height, width=width)
    with sd_lock:
        latest_sd_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        sd_img_ready = True
        cv2.imwrite(filename, latest_sd_img)

def main_loop():
    global latest_sd_img, sd_img_ready, yolo_enabled, obj_boxes
    cam = Camera(0)
    yolo = ObjectDetector(device=device)
    emo = EmotionDetector()

    try:
        while True:
            frame = cam.get_frame()
            emotions = emo.analyze(frame)
            update_emotion_counter(emotions)

            if is_reset_requested():
                with sd_lock:
                    latest_sd_img = None
                    sd_img_ready = False
                    yolo_enabled = False
                    obj_boxes = []
                clear_emotions()
                clear_reset_flag()

            if is_emotion_triggered() or is_text_triggered():
                yolo_enabled = True

            if is_sd_generation_requested():
                if is_emotion_triggered():
                    prompt = generate_prompt_from_top_emotion()
                    filename = "emotion_frame.jpg"
                elif is_text_triggered():
                    prompt = get_latest_prompt()
                    filename = "text_frame.jpg"
                else:
                    prompt = "a neutral background"
                    filename = "default_frame.jpg"
                threading.Thread(target=generate_sd_background, args=(prompt, frame.shape[0], frame.shape[1], filename), daemon=True).start()
                reset_triggers()
                clear_sd_generation_flag()

            if yolo_enabled:
                obj_boxes = yolo.detect(frame)

            if latest_sd_img is not None:
                with sd_lock:
                    bg = latest_sd_img.copy()
                mask = np.ones(frame.shape, dtype=np.uint8) * 255
                for b in obj_boxes:
                    mask[b.y1:b.y2, b.x1:b.x2] = frame[b.y1:b.y2, b.x1:b.x2]
                frame = np.where(mask == 255, bg, mask)

            Overlay.draw(frame, obj_boxes + emotions)

            cv2.imshow('Immersive Environment', frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        cam.release()
        cv2.destroyAllWindows()

def start_server():
    uvicorn.run("server:app", host="0.0.0.0", port=8000)

if __name__ == '__main__':
    threading.Thread(target=start_server, daemon=True).start()
    main_loop()
