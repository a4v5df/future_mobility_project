import cv2
import numpy as np
import threading
from camera.capture import Camera
from server.detectors.emotion_detector import EmotionDetector
from visualizers.overlay import Overlay
from generators.sd_generator import SDGenerator
import uvicorn
import time
from emotion_state import update_emotion_counter, generate_prompt_from_top_emotion, clear_emotions
from server import is_emotion_triggered, is_text_triggered, get_latest_prompt, reset_triggers, is_reset_requested, clear_reset_flag, is_sd_generation_requested, clear_sd_generation_flag

# YOLO 모드 선택
DETECTION_MODE = 'seg'  # 'box' or 'seg'
device = 'cpu'

# YOLO detector 분기 로딩
if DETECTION_MODE == 'box':
    from server.detectors.box_object_detector import ObjectDetector as YoloDetector
elif DETECTION_MODE == 'seg':
    from server.detectors.segment_object_detector import SegmentationDetector as YoloDetector
else:
    raise ValueError("DETECTION_MODE must be 'box' or 'seg'.")

# 글로벌 변수 초기화
sd_img_ready = False
latest_sd_img = None
sd_lock = threading.Lock()
yolo_enabled = False
obj_boxes = []

def generate_sd_background(sd, prompt, height, width):
    global latest_sd_img, sd_img_ready
    img = sd.generate_image(prompt, height=height, width=width)
    with sd_lock:
        latest_sd_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        sd_img_ready = True

def main_loop():
    global latest_sd_img, sd_img_ready, yolo_enabled, obj_boxes
    cam = Camera(0)
    yolo = YoloDetector(device=device)
    emo = EmotionDetector()
    sd = SDGenerator(device=device)

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
                elif is_text_triggered():
                    prompt = get_latest_prompt()
                else:
                    prompt = "a neutral background"

                threading.Thread(
                    target=generate_sd_background,
                    args=(sd, prompt, frame.shape[0], frame.shape[1]),
                    daemon=True
                ).start()

                reset_triggers()
                clear_sd_generation_flag()

            if yolo_enabled:
                obj_boxes = yolo.detect(frame)

            if latest_sd_img is not None:
                with sd_lock:
                    bg = latest_sd_img.copy()

                # seg 모드에서는 마스크 직접 사용할 수 있으므로 이 부분 조건 분기 가능
                mask = np.ones(frame.shape, dtype=np.uint8) * 255
                for b in obj_boxes:
                    if hasattr(b, 'mask') and b.mask is not None:
                        binary_mask = (b.mask * 255).astype(np.uint8)
                        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        cv2.drawContours(bg, contours, -1, (0, 255, 0), -1)
                    else:
                        mask[b.y1:b.y2, b.x1:b.x2] = frame[b.y1:b2, b.x1:b.x2]
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
