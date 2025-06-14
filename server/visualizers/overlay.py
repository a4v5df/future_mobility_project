import cv2
import numpy as np
from typing import List, Tuple
from detectors.types import Box

class Overlay:
    @staticmethod
    def get_color(label: str, seed: str = "") -> Tuple[int, int, int]:
        h = (abs(hash(seed + label)) % 180)
        hsv_color = np.uint8([[[h, 200, 200]]])
        bgr_color = cv2.cvtColor(hsv_color, cv2.COLOR_HSV2BGR)[0][0]
        return int(bgr_color[0]), int(bgr_color[1]), int(bgr_color[2])

    @staticmethod
    def draw(frame, boxes: List[Box]):
        for b in boxes:
            color = Overlay.get_color(b.label)
            cv2.rectangle(frame, (b.x1, b.y1), (b.x2, b.y2), color, 2)
            cv2.putText(
                frame,                          # 이미지 프레임
                f"{b.label}:{b.score:.2f}",     # 텍스트 내용
                (b.x1, b.y1 - 10),              # 텍스트 위치 (좌측 상단보다 약간 위)
                cv2.FONT_HERSHEY_SIMPLEX,       # 폰트 종류
                0.5,                            # 폰트 크기 (스케일)
                color,                          # 텍스트 색상 (BGR)
                1                               # 두께 (굵기)
            )