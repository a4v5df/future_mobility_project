from ultralytics import YOLO
from detectors.types import SegBox
from detectors.base_detector import BaseDetector
from typing import List
import numpy as np

class SegmentationDetector(BaseDetector):
    def __init__(self, model_path='yolov8m-seg.pt', device='cpu'):
        self.model = YOLO(model_path)
        self.model.to(device)

    def detect(self, frame: np.ndarray) -> List[SegBox]:
        results = self.model(frame, verbose=False)[0]
        if results.masks is None:
            return []
        masks = results.masks.data.cpu().numpy()
        boxes = []
        for i, box in enumerate(results.boxes):
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            cls_id = int(box.cls[0])
            label = results.names[cls_id]
            score = float(box.conf[0])
            mask = masks[i]
            boxes.append(SegBox(x1, y1, x2, y2, label, score, mask))
        return boxes
