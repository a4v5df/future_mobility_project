import cv2
import numpy as np
from camera.capture import Camera
from detectors.yolo_detector import YOLODetector
from detectors.fer_detector import FERDetector
from visualizers.overlay import Overlay
from generators.sd_generator import SDGenerator

def main():
    cam = Camera(0)
    yolo = YOLODetector('yolov8m.pt', device='cpu')
    fer  = FERDetector(mtcnn=True)
    sd   = SDGenerator(device='cpu')
    try:
        while True:
            frame = cam.get_frame()
            boxes = yolo.detect(frame)
            emotions = fer.analyze(frame, boxes)
            Overlay.draw(frame, boxes, emotions)

            if emotions:
                prompt = sd.generate_prompt(emotions[0].emotion)
                sd_img = sd.generate_image(prompt, height=128, width=128)
                # 생성된 이미지를 frame 오른쪽 위에 붙이기
                h, w = sd_img.size
                sd_np = cv2.cvtColor(np.array(sd_img), cv2.COLOR_RGB2BGR)
                frame[0:h, -w:] = sd_np

            cv2.imshow('YOLO + FER', frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        cam.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
