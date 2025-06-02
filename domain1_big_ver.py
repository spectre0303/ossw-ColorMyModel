import cv2                      # OpenCV: 이미지 처리, 윤곽선 추출, 블러, 필터 등 제공
import numpy as np              # NumPy: 이미지 배열 연산, 마스크 처리 등 수치 연산용
from PIL import Image           # Pillow: 이미지 파일 열기 및 그레이스케일 변환
from sklearn.cluster import KMeans  # scikit-learn: KMeans를 통한 이미지 영역 분할 (클러스터링)
import pytesseract              # Tesseract OCR: 이미지에서 텍스트 추출
import re                       # 정규표현식: OCR 문자열에서 특정 라벨 패턴 추출
import random                   # 무작위 색상 생성 (label별 색상 매핑)
import csv                      # CSV 파일 저장용 (라벨-색상 대응표 저장)
import colorsys                # 색상 변환 (HSV -> RGB
#라이브러리 모두 상업적 사용 가능

# 구분 잘되는 랜덤 색상 생성 함수
def generate_distinct_colors(n, sat_range=(0.4, 0.8), val_range=(0.6, 0.9)):
    colors = set()
    max_attempts = 1000  # 무한 루프 방지용

    attempts = 0
    i = 0
    while len(colors) < n and attempts < max_attempts:
        h = i / n
        s = random.uniform(*sat_range)
        v = random.uniform(*val_range)
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        rgb = (int(r * 255), int(g * 255), int(b * 255))

        if rgb not in colors:
            colors.add(rgb)
            i += 1
        else:
            attempts += 1  # 중복이면 다시 시도 (i는 유지)

    if len(colors) < n:
        print(f"⚠️ 중복 회피 실패: {n}개 중 {len(colors)}개만 생성됨.")
    return list(colors)

#외곽 윤곽선 내부 마스크 추출 함수
def extract_external_mask(
    input_img: np.ndarray,
    lap_blur: np.ndarray,
    morph_kernel_size: tuple = (7, 7),
    remove_large_threshold: float = 0.6
) -> np.ndarray:
    """
        input_img: 입력 그레이스케일 이미지
        lap_blur: 블러하거나 안된, 윤곽선 추출을 위한 이미지
        morph_kernel_size: 형태학 연산용 커널 크기 (ex. (7,7))
        remove_large_threshold: 삭제할 외곽 비율 기준 (ex. 0.6 → 60%)

    Returns:
        external_mask: 외곽선 내부 영역이 흰색(255)인 마스크 이미지
    """

    # 1. Laplacian edge detection
    laplacian = cv2.Laplacian(lap_blur, cv2.CV_8U, ksize=3)
    _, edge_mask = cv2.threshold(laplacian, 25, 255, cv2.THRESH_BINARY)

    # 2. 형태학적 닫기 연산
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, morph_kernel_size)
    edge_mask_closed = cv2.morphologyEx(edge_mask, cv2.MORPH_CLOSE, kernel)

    # 3. 너무 큰 외곽선 제거
    image_area = input_img.shape[0] * input_img.shape[1]
    while True:
        contours_ext, _ = cv2.findContours(edge_mask_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        found_large_contour = False
        for cnt in contours_ext:
            cnt_area = cv2.contourArea(cnt)
            if (cnt_area / image_area) >= remove_large_threshold:
                cv2.drawContours(edge_mask_closed, [cnt], -1, 0, 1)
                found_large_contour = True
        if not found_large_contour:
            break

    # 4. 외곽선 내부 마스크 생성
    contours_ext, _ = cv2.findContours(edge_mask_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    external_mask = np.zeros_like(input_img)
    for cnt in contours_ext:
        if cv2.contourArea(cnt) > 30:
            cv2.drawContours(external_mask, [cnt], -1, 255, -1)

    external_mask = cv2.morphologyEx(external_mask, cv2.MORPH_CLOSE, kernel)

    return external_mask

#----------------------------------------------------------------------------시작
# === 설정 ===
label_mode = 1  # 0: 숫자, 1: XF-숫자, X-숫자, TS-숫자, 2: H숫자, 3: 문자형식
save_label_color_map = True
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# === 이미지 불러오기 ===
img_path = r"C:\Users\LG\Desktop\학교\SW프젝\ex4.jpg"  # 이미지 경로
img_pil = Image.open(img_path).convert("L")
img_gray = np.array(img_pil)

# 이미지 해상도 체크. 너무 낮을 경우 받지 않음.
width, height = img_pil.size
if width > height or width == height:
    if width < 1000 or height < 500:
        print("이미지 해상도가 너무 낮습니다. 최소 1000X500 픽셀 이상이어야 합니다.")
        exit()
else:
    if width < 500 or height < 1000:
        print("이미지 해상도가 너무 낮습니다. 최소 500X1000 픽셀 이상이어야 합니다.")
        exit()

#이미지 크기가 너무 큰경우 리사이즈(최대 1800)
h, w = img_gray.shape[:2]
if h > 1800 or w > 1800:
    if h >= w:
        scale = 1800 / h
    else:
        scale = 1800 / w

    # 리사이즈 후 크기 계산
    new_h = int(h * scale)
    new_w = int(w * scale)

    # numpy array를 OpenCV가 인식할 수 있도록 리사이즈
    resized_img = cv2.resize(img_gray, (new_w, new_h), interpolation=cv2.INTER_AREA)
else:
    resized_img = img_gray
ocr_text = pytesseract.image_to_string(resized_img, config='--psm 6')

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
    num_regions = 5
    unique_labels = [f"Region_{i+1}" for i in range(num_regions)]

#------------------------------윤곽선 추출---------------------------------------------
binary_adapt = cv2.adaptiveThreshold(
    resized_img,
    maxValue=255,
    adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    thresholdType=cv2.THRESH_BINARY,
    blockSize=21,  
    C=2              # 평균–2 만큼 이동
)

cv2.imwrite("binary_adaptive.png", binary_adapt)

laplacian = cv2.Laplacian(binary_adapt, cv2.CV_8U, ksize=3)
_, edge_mask = cv2.threshold(laplacian, 25, 255, cv2.THRESH_BINARY)

cv2.imwrite("edge_mask.png", edge_mask)

num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(edge_mask, connectivity=8)

# 2) 새 마스크 생성
mask = np.zeros_like(resized_img)

# 3) 최소 기준 정의
MIN_AREA     = 100   # 너무 작은 덩어리 제거
MIN_RATIO    = 3.0    # 긴 직선: w/h 또는 h/w가 이 이상
MIN_LENGTH   = 10     # 최소 길이(px) – w 또는 h가 이 이상

for lbl in range(1, num_labels):
    x, y, w, h, area = stats[lbl]
    if area < MIN_AREA:
        continue
    # 긴 직선 비율
    ratio = max(w/h if h>0 else 0, h/w if w>0 else 0)
    if ratio < MIN_RATIO:
        continue
    if max(w, h) < MIN_LENGTH:
        continue
    # 조건 통과 시 그 부분만 살리기
    mask[labels == lbl] = 255

thinned = cv2.ximgproc.thinning(mask) 

cv2.imwrite("cc_filtered.png", thinned)

avg_filled = resized_img.copy()
ys, xs = np.where(thinned == 255)
h, w = img_gray.shape[:2]
for x, y in zip(xs, ys):
    x0, x1 = max(x - 1, 0), min(x + 2, w)
    y0, y1 = max(y - 1, 0), min(y + 2, h)

    if y1 > y0 and x1 > x0:
        region = resized_img[y0:y1, x0:x1]
        if region.size > 0:
            brightest = int(np.max(region))
            brightest = np.max(region)
            avg_filled[y, x] = brightest # 가장 밝은 값으로 1픽셀 점 그리기

quantized = (avg_filled // 32) * 32

lap_blur = cv2.GaussianBlur(avg_filled, (3, 3), 0)
external_mask= extract_external_mask(#average filled를 이용한 외곽선 내부 마스크 추출
    input_img=resized_img,
    lap_blur=lap_blur,
    morph_kernel_size=(9, 9),
    remove_large_threshold=0.6
)

external_mask2 = extract_external_mask( #thinned를 이용한 외곽선 내부 마스크 추출
    input_img=resized_img,
    lap_blur=thinned,
    morph_kernel_size=(3, 3),
    remove_large_threshold=0.6
)

external_mask[external_mask2 == 0] = 0 #external_mask-external_mask2
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
colors = generate_distinct_colors(num_regions)
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
#이거 안하면 점점이 겁나 안이쁨
b, g, r = cv2.split(color_image)
b_blur = cv2.medianBlur(b, 3)
g_blur = cv2.medianBlur(g, 3)
r_blur = cv2.medianBlur(r, 3)
blurred_color_image = cv2.merge([b_blur, g_blur, r_blur])

#윤곽선을 thinned로 투명도 80퍼센트로 그리기
overlay = blurred_color_image.copy()
overlay[thinned == 255] = (0, 0, 0)
alpha = 0.8
blended = cv2.addWeighted(overlay, alpha, blurred_color_image, 1 - alpha, 0)


# === 결과 저장
cv2.imwrite("before_color.png", quantized) #랜덤 채색 이전, 윤곽선 거의 없애거나 흐릿하게 만들고 명암 등급화한 상태태
cv2.imwrite("1result_color_segmented.png", blurred_color_image )
cv2.imwrite("2final_overlay.png", blended)

#--------------------------------명암에 따른 영역 분리 끝----------------------------------------------------
''''''