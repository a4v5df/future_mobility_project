import cv2
import threading
from PIL import Image
import numpy as np

def show_image_overlay(image_path: str):
    def run():
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("❌ 카메라를 열 수 없습니다.")
            return

        # Stable Diffusion 이미지 불러오기 (PIL → numpy 변환)
        overlay_image = Image.open(image_path).convert("RGB")
        overlay_image = overlay_image.resize((640, 480))  # 영상 사이즈에 맞게 조절
        overlay_np = np.array(overlay_image)

        alpha = 0.4  # 오버레이 강도 (0=없음, 1=덮어쓰기)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 오버레이 이미지 적용
            blended = cv2.addWeighted(frame, 1 - alpha, overlay_np, alpha, 0)

            cv2.imshow("Overlay Video", blended)

            # q를 누르면 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    # 영상 처리를 백그라운드 스레드에서 실행
    threading.Thread(target=run).start()
