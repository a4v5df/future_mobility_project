# from ultralytics import YOLO
# from typing import List
# from detectors.types import Box  

# class ObjectDetector:
#     def __init__(self, model_path: str = 'yolov8m.pt', device: str = 'cpu'):
#         self.model = YOLO(model_path)
#         self.model.to(device)

#     def detect(self, frame) -> List[Box]:
#         results = self.model(frame, 
#                              verbose=False # 로그 제거
#                              )[0]
#         boxes: List[Box] = []
#         for box in results.boxes:
#             x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
#             cls_id = int(box.cls[0])
#             label = results.names[cls_id]
#             score = float(box.conf[0])
#             boxes.append(Box(x1, y1, x2, y2, label, score))
#         return boxes

from ultralytics import YOLO
from detectors.types import Box
from detectors.base_detector import BaseDetector
from typing import List
import numpy as np

class ObjectDetector(BaseDetector):
    def __init__(self, model_path='yolov8m.pt', device='cpu'):
        self.model = YOLO(model_path)
        self.model.to(device)

    def detect(self, frame: np.ndarray) -> List[Box]:
        results = self.model(frame, verbose=False)[0]
        boxes = []
        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            cls_id = int(box.cls[0])
            label = results.names[cls_id]
            score = float(box.conf[0])
            boxes.append(Box(x1, y1, x2, y2, label, score))
        return boxes
