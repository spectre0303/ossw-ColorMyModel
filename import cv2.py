import cv2                      # OpenCV: 이미지 처리, 윤곽선 추출, 블러, 필터 등 제공
import numpy as np              # NumPy: 이미지 배열 연산, 마스크 처리 등 수치 연산용
from PIL import Image           # Pillow: 이미지 파일 열기 및 그레이스케일 변환
from sklearn.cluster import KMeans  # scikit-learn: KMeans를 통한 이미지 영역 분할 (클러스터링)
import pytesseract              # Tesseract OCR: 이미지에서 텍스트 추출
import re                       # 정규표현식: OCR 문자열에서 특정 라벨 패턴 추출
import random                   # 무작위 색상 생성 (label별 색상 매핑)
import csv                      # CSV 파일 저장용 (라벨-색상 대응표 저장)
#아 여기 위에 라이브러리 모두 상업적 사용 가능


# === 설정 ===
label_mode = 1   # 0: 숫자, 1: XF-숫자, X-숫자, TS-숫자, 2: H숫자, 3: 문자형식
save_label_color_map = True
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# === 이미지 불러오기 ===
img_path = r"C:/Users/hongc/Desktop/CS/Projects/Test_img_LowRes.jpg"
img_pil = Image.open(img_path).convert("L")
img_gray = np.array(img_pil)

# 이미지 해상도 체크. 너무 낮을 경우 받지 않음.
width, height = img_pil.size
if width < 1000 or height < 1000:
    print("이미지 해상도가 너무 낮습니다. 최소 1000x1000 픽셀 이상이어야 합니다.")
    exit()

ocr_text = pytesseract.image_to_string(img_gray, config='--psm 6')

print("===== OCR 추출 결과 전체 보기 =====") #해보니 지금 안나온 내용이 꽤 있음.
print(ocr_text)
print("===== 끝 =====")

# === 라벨 추출 === --> 여기 어차피 나중에 OCR 매핑 해야하니까 그때 추가 수정. 지금 이건 이런 방식으로 OCR을 통해 영역의 개수를 가져올 것이다. 라는것.
if label_mode == 0:
    found_labels = [s for s in ocr_text.split() if s.isdigit()]
elif label_mode == 1:
    found_labels = re.findall(r'(XF-\d+|X-\d+|TS-\d+)', ocr_text)
elif label_mode == 2:
    found_labels = re.findall(r'H\d+', ocr_text)
elif label_mode == 3:
    raw = re.findall(r'[A-Za-z]+(?:\s+[A-Za-z]+)?(?:\(\d+\))?', ocr_text)
    found_labels = []
    for word in raw:
        cleaned = re.sub(r'\(\d+\)', '', word).strip()
        if len(cleaned) > 1 and not any(char.isdigit() for char in cleaned):
            found_labels.append(cleaned)
else:
    found_labels = []

# === 라벨 중복 제거 및 정렬 ===
unique_labels = sorted(set(found_labels), key=lambda x: str(x).lower())
num_regions = len(unique_labels)
if num_regions == 0:
    num_regions = 7
    unique_labels = [f"Region_{i+1}" for i in range(num_regions)]

# === 윤곽선 추출 및 원본 회색값으로 선 채색
blurred = cv2.GaussianBlur(resized_img, (3, 3), 0)
edges = cv2.Canny(blurred, 50, 150)
kernel = np.ones((3, 3), np.uint8)

contours_all, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

avg_filled = resized_img.copy()

for cnt in contours_all:
    for point in cnt:
        x, y = point[0]
        gray_val = resized_img[y, x]
        cv2.circle(avg_filled, (x, y), 1, int(gray_val), -1)  # 1픽셀 회색 점 찍기

# === 양자화
quantized = (avg_filled // 32) * 32

##===============================외곽 윤곽선 과정
# === 윤곽선 추출 및 이어주기
lap_blur = cv2.GaussianBlur(quantized, (3, 3), 0)
laplacian = cv2.Laplacian(lap_blur, cv2.CV_8U, ksize=3)
_, edge_mask = cv2.threshold(laplacian, 25, 255, cv2.THRESH_BINARY)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
edge_mask_closed = cv2.morphologyEx(edge_mask, cv2.MORPH_CLOSE, kernel)

# === 60% 이상인 외곽 윤곽선이 없을 때까지 반복적으로 제거
image_area = resized_img.shape[0] * resized_img.shape[1]
while True:
    # 외곽 윤곽선 찾기
    contours_ext, _ = cv2.findContours(edge_mask_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    found_large_contour = False

    # 윤곽선 중 60% 이상인 것 삭제
    for cnt in contours_ext:
        cnt_area = cv2.contourArea(cnt)
        if (cnt_area / image_area) >= 0.6:
            cv2.drawContours(edge_mask_closed, [cnt], -1, 0, 1)  # 해당 윤곽선만을 검정색(0)으로 지움
            found_large_contour = True

    # 더 이상 삭제할 큰 윤곽선이 없으면 종료
    if not found_large_contour:
        break

# === 외곽 윤곽선 추출
contours_ext, _ = cv2.findContours(edge_mask_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#== 외곽선 내부만 흰색인 마스크
external_mask = np.zeros_like(edge_mask)
for cnt in contours_ext:
    if cv2.contourArea(cnt) > 30:
        cv2.drawContours(external_mask, [cnt], -1, 255, -1)

external_mask = cv2.morphologyEx(external_mask, cv2.MORPH_CLOSE, kernel)
##===============================외곽 윤곽선 끝

# === KMeans 분할
# === 외곽 내부 영역만 추출 (원본 grayscale 기준)
masked_pixels = quantized[external_mask == 255]
h, w = quantized.shape
Z = masked_pixels.reshape((-1, 1)).astype(np.float32)
kmeans = KMeans(n_clusters=num_regions, n_init=10)
kmeans.fit(Z)
labels_full = np.full(quantized.shape, -1, dtype=np.int32)

# 외곽 내부에만 결과 매핑
labels_full[external_mask == 255] = kmeans.labels_

# === 색상 매핑
color_image = np.full((h, w, 3), 255, dtype=np.uint8)
colors = [tuple(random.randint(0, 255) for _ in range(3)) for _ in range(num_regions)]
for i in range(num_regions):
    color_image[labels_full == i] = colors[i]

# === 라벨-색상 매핑 저장 --> 이건 나중에 OCR 매핑할때 사용. 지금은 그냥 랜덤으로 부여된 색상 저장되어있음
if save_label_color_map:
    with open("label_color_mapping.csv", "w", newline="", encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Label", "R", "G", "B"])
        for label, color in zip(unique_labels, colors):
            writer.writerow([label] + list(color))

# === 색상 블러 처리
b, g, r = cv2.split(color_image)
b_blur = cv2.medianBlur(b, 3)
g_blur = cv2.medianBlur(g, 3)
r_blur = cv2.medianBlur(r, 3)
blurred_color_image = cv2.merge([b_blur, g_blur, r_blur])

# === 결과 저장
cv2.imwrite("outer.png", edge_mask_closed)
cv2.imwrite("before_color.png", quantized)
cv2.imwrite("1result_color_segmented.png", blurred_color_image )
