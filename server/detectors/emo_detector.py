import cv2
from deepface import DeepFace
from typing import List
from detectors.types import Box 

class EmotionDetector:
    def __init__(self):
        pass

    def analyze(self, frame) -> List[Box]:
        results: List[Box] = []
        h_frame, w_frame = frame.shape[:2]

        try:
            analysis = DeepFace.analyze(
                                            frame,
                                            actions=['emotion'],
                                            enforce_detection=False,
                                            detector_backend='ssd',  # ← opencv 백엔드 사용
                                        )
            faces = analysis if isinstance(analysis, list) else [analysis]

            for face_data in faces:
                region = face_data['region']
                x1 = max(0, region['x'])
                y1 = max(0, region['y'])
                x2 = min(w_frame, x1 + region['w'])
                y2 = min(h_frame, y1 + region['h'])

                emotion = face_data['dominant_emotion']
                score = face_data['emotion'][emotion]

                results.append(Box(x1, y1, x2, y2, label=emotion, score=score))
                print(f"[DETECT] {emotion} ({score:.2f}) at ({x1},{y1}) to ({x2},{y2})")

        except Exception as e:
            print(f"[DeepFace] 감정 분석 오류: {e}")

        return results
