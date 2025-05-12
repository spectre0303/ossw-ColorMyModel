import cv2                      # OpenCV: 이미지 처리, 윤곽선 추출, 블러, 필터 등 제공
import numpy as np              # NumPy: 이미지 배열 연산, 마스크 처리 등 수치 연산용
from PIL import Image           # Pillow: 이미지 파일 열기 및 그레이스케일 변환

def preprocessImg(img_path):
    # === 이미지 불러오기 ===
    img_pil = Image.open(img_path).convert("L")
    img_gray = np.array(img_pil)

    # 이미지 해상도 체크. 너무 낮을 경우 받지 않음.
    width, height = img_pil.size
    if width < 1000 or height < 1000:
        print("이미지 해상도가 너무 낮습니다. 최소 1000x1000 픽셀 이상이어야 합니다.")
        return False
    
    
    
