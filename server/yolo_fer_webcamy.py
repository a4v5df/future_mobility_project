import cv2
from ultralytics import YOLO
from fer import FER

# 모델 불러오기
model = YOLO("yolov8m.pt")  
detector = FER(mtcnn=False)

# 카메라 열기
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # YOLO 객체 탐지
    results = model(frame)[0]

    for box in results.boxes:
        cls_id = int(box.cls[0])
        class_name = model.names[cls_id]
        if class_name != 'person':
            continue

        # 박스 좌표 추출
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        face_crop = frame[y1:y2, x1:x2]

        # 감정 분석
        emotions = detector.detect_emotions(face_crop)
        label = ""
        if emotions:
            top_emotion, score = max(emotions[0]["emotions"].items(), key=lambda x: x[1])
            label = f"{top_emotion} ({score:.2f})"

        # 시각화
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        if label:
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # 결과 출력
    cv2.imshow("YOLO + FER", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC 누르면 종료
        break

cap.release()
cv2.destroyAllWindows()
