import cv2
import numpy as np
from typing import List, Tuple
from detectors.yolo_detector import Box
from detectors.fer_detector import EmotionResult

class Overlay:
    @staticmethod
    def get_color(label: str, seed: str = "") -> Tuple[int, int, int]:
        # Generate a distinct BGR color via HSV mapping
        h = (abs(hash(seed + label)) % 180)  # Hue range [0,179]
        hsv_color = np.uint8([[[h, 200, 200]]])  # S=200, V=200
        bgr_color = cv2.cvtColor(hsv_color, cv2.COLOR_HSV2BGR)[0][0]
        return int(bgr_color[0]), int(bgr_color[1]), int(bgr_color[2])

    @staticmethod
    def draw(frame, boxes: List[Box], emotions: List[EmotionResult]):
        # Draw YOLO-detected boxes with class-specific colors
        for b in boxes:
            color = Overlay.get_color(b.label, seed="obj_")
            cv2.rectangle(frame, (b.x1, b.y1), (b.x2, b.y2), color, 2)
            cv2.putText(
                frame,
                f"{b.label}:{b.score:.2f}",
                (b.x1, b.y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1
            )
        # Draw FER emotion boxes and labels
        for e in emotions:
            color = Overlay.get_color(e.emotion, seed="emo_")
            # Draw rectangle around detected face region
            cv2.rectangle(frame, (e.box.x1, e.box.y1), (e.box.x2, e.box.y2), color, 2)
            # Draw emotion text below the box
            x, y = e.box.x1, e.box.y2 + 20
            text = f"{e.emotion}:{e.score:.2f}"
            cv2.putText(
                frame,
                text,
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )