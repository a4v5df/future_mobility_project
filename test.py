import cv2
from fer import FER

# 감정 분석기 초기화
detector = FER(mtcnn=False)  # 얼굴 감지 정확도 향상 (조금 느릴 수 있음)

# 웹캠 열기
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ 카메라 열기 실패")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 감정 분석 수행
    results = detector.detect_emotions(frame)

    for r in results:
        (x, y, w, h) = r["box"]
        top_emotion, score = max(r["emotions"].items(), key=lambda item: item[1])

        # 얼굴 사각형 그리기
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # 감정 텍스트 표시
        label = f"{top_emotion} ({score:.2f})"
        cv2.putText(frame, label, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    # 영상 출력
    cv2.imshow("Real-time Emotion Detection", frame)

    # 'q' 키 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 종료 처리
cap.release()
cv2.destroyAllWindows()
