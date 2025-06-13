import cv2
from fer import FER
from typing import NamedTuple, List
from detectors.yolo_detector import Box

class EmotionResult(NamedTuple):
    box: Box
    emotion: str
    score: float

class FERDetector:
    def __init__(self, mtcnn: bool = True):
        self.detector = FER(mtcnn=mtcnn)

    def analyze(self, frame, boxes: List[Box]) -> List[EmotionResult]:
        results: List[EmotionResult] = []
        for b in boxes:
            if b.label != 'person':
                continue
            x1, y1, x2, y2 = b.x1, b.y1, b.x2, b.y2
            face = frame[y1:y2, x1:x2]
            if face.size == 0:
                continue
            emotions = self.detector.detect_emotions(face)
            if not emotions:
                continue
            top_emotion = max(emotions[0]['emotions'].items(), key=lambda x: x[1])
            emotion, score = top_emotion
            results.append(EmotionResult(box=b, emotion=emotion, score=score))
        return results
