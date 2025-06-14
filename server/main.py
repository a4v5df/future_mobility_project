import cv2
import numpy as np
import threading
from camera.capture import Camera
from detectors.obj_detector import ObjectDetector
from detectors.emo_detector import EmotionDetector
from visualizers.overlay import Overlay
from generators.sd_generator import SDGenerator
from collections import Counter
from server import latest_prompt, emotion_triggered, text_triggered
import uvicorn

emotion_counter = Counter()


def main_loop():
    device = 'cuda'
    cam = Camera(0)
    yolo = ObjectDetector(device=device)
    emo = EmotionDetector()
    sd = SDGenerator(device=device)

    try:
        while True:
            frame = cam.get_frame()
            emotions = emo.analyze(frame)
            for e in emotions:
                emotion_counter[e.label] += 1

            # 감정 기반 배경 처리
            if emotion_triggered:
                top_emotion = emotion_counter.most_common(1)[0][0]
                prompt = sd.generate_prompt(top_emotion)
                sd_img = sd.generate_image(prompt, height=frame.shape[0], width=frame.shape[1])
                obj_boxes = yolo.detect(frame)
                mask = np.ones(frame.shape, dtype=np.uint8) * 255
                for b in obj_boxes:
                    mask[b.y1:b.y2, b.x1:b.x2] = frame[b.y1:b.y2, b.x1:b.x2]
                bg = cv2.cvtColor(np.array(sd_img), cv2.COLOR_RGB2BGR)
                frame = np.where(mask == 255, bg, mask)
                Overlay.draw(frame, obj_boxes, emotions)            
                emotion_counter.clear()


            # 텍스트 기반 배경 처리
            elif text_triggered and latest_prompt:

                sd_img = sd.generate_image(latest_prompt, height=frame.shape[0], width=frame.shape[1])
                obj_boxes = yolo.detect(frame)
                mask = np.ones(frame.shape, dtype=np.uint8) * 255
                for b in obj_boxes:
                    mask[b.y1:b.y2, b.x1:b.x2] = frame[b.y1:b.y2, b.x1:b.x2]
                bg = cv2.cvtColor(np.array(sd_img), cv2.COLOR_RGB2BGR)
                frame = np.where(mask == 255, bg, mask)
                Overlay.draw(frame, obj_boxes, emotions)        
                emotion_counter.clear()

            else:
                Overlay.draw(frame, emotions)

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
