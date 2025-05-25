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
label_mode = 1  # 0: 숫자, 1: XF-숫자, X-숫자, TS-숫자, 2: H숫자, 3: 문자형식
save_label_color_map = True
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# === 이미지 불러오기 ===
img_path = r"C:\Users\LG\Desktop\학교\SW프젝\KakaoTalk_20250508_134842636.jpg"
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

#--------------------------------명암에 따른 영역 분리 끝----------------------------------------------------
#-------------------------------라벨 + 랜덤 색상 매핑 시작--------------------------------

MIN_LENGTH = 50  # 최소 선 길이

# === 라벨 위치 추출 ===
label_positions = {} # 라벨 위치를 저장할 딕셔너리
with open("label_color_mapping.csv", "r", newline="", encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    labels = [row[0] for row in reader]

data = pytesseract.image_to_data(resized_img, lang='eng', output_type=pytesseract.Output.DICT)
seen = set() #라벨 위치 첫번째 발견 후 중복 방지
for i, text in enumerate(data['text']):
    txt = text.strip()
    if txt in labels and txt not in seen:
        x, y = data['left'][i], data['top'][i]
        w_box, h_box = data['width'][i], data['height'][i]
        # 라벨 영역 중앙 좌표
        label_positions[txt] = (x + w_box//2, y + h_box//2)
        seen.add(txt)
        print(f"{txt}: 위치 = {label_positions[txt]}")


# -------------- 전처리 이진화 -----------------

binary_adapt = cv2.adaptiveThreshold(
    resized_img,
    maxValue=255,
    adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    thresholdType=cv2.THRESH_BINARY,
    blockSize=21,   # 15×15 픽셀 블록 단위
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
MIN_AREA     = 100    # 너무 작은 덩어리 제거
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

cv2.imwrite("cc_filtered.png", mask)

# -------------- 직선 찾기 시작
lines_p = cv2.HoughLinesP(mask, rho=1, theta=np.pi/180, threshold=50,
                          minLineLength=MIN_LENGTH, maxLineGap=5)
segments = []
if lines_p is not None:
    for l in lines_p:
        x1,y1,x2,y2 = l[0]
        segments.append(((x1,y1),(x2,y2)))
# --- Hough 결과 시각화 ---
hough_img = cv2.cvtColor(resized_img, cv2.COLOR_GRAY2BGR)
for (x1,y1),(x2,y2) in segments:
    cv2.line(hough_img, (x1,y1), (x2,y2), (0,255,0), 1)
cv2.imwrite("hough_lines.png", hough_img)


chosen_segments = {} #for 시각화
actual_colors = {}
for label, (px, py) in label_positions.items():
    # 선분과 라벨 거리 계산
    segs = []
    for seg in segments:
        (x1,y1),(x2,y2) = seg
        d1 = np.hypot(px-x1, py-y1)
        d2 = np.hypot(px-x2, py-y2)
        if d1 < d2:
            near, far = (x1,y1),(x2,y2)
            dist = d1
        else:
            near, far = (x2,y2),(x1,y1)
            dist = d2
        segs.append((dist, near, far, seg))
    # 거리순 정렬
    segs.sort(key=lambda x: x[0])
    found = False
    for dist, near, far, seg in segs:
        fx, fy = far
        # 반대 끝점 주변 3x3에 외곽 마스크 존재 확인
        ok = False
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                nx, ny = fx+dx, fy+dy
                if 0 <= nx < external_mask.shape[1] and 0 <= ny < external_mask.shape[0]:
                    if external_mask[ny,nx] != 0:
                        ok = True
                        break
            if ok: break
        if not ok:
            continue
        # 기울기 계산 및 유사 기울기 병합
        x1,y1 = near; x2,y2 = far
        slope1 = np.inf if x2==x1 else (y2-y1)/(x2-x1)
        max_far = far
        for seg2 in segments:
            (u1,v1),(u2,v2) = seg2
            slope2 = np.inf if u2==u1 else (v2-v1)/(u2-u1)
            if abs(slope2 - slope1) < 0.01:
                # 더 먼 끝점 선택
                d_21 = np.hypot(u1-x1, v1-y1)
                d_22 = np.hypot(u2-x1, v2-y1)
                cand = (u1,v1) if d_21>d_22 else (u2,v2)
                if np.hypot(cand[0]-x1, cand[1]-y1) > np.hypot(max_far[0]-x1, max_far[1]-y1):
                    max_far = cand
        fx, fy = max_far
        # 최종 외곽 내부 확인 (반대쪽 끝점 주변 3×3 영역 확인)
        ok2 = False
        for dx2 in (-1, 0, 1):
            for dy2 in (-1, 0, 1):
                nx2, ny2 = fx + dx2, fy + dy2
                if 0 <= nx2 < external_mask.shape[1] and 0 <= ny2 < external_mask.shape[0]:
                    if external_mask[ny2, nx2] != 0:
                        ok2 = True
                        break
            if ok2:
                break
        if not ok2:
            # 주변 어느 곳에도 외곽 내부가 없으면 다음 선분으로
            continue
        # 색상 추출 (BGR)
        chosen_segments[label] = seg
        b, g, r = blurred_color_image[fy, fx]
        actual_colors[label] = (int(r), int(g), int(b))
        found = True
        break
    if not found:
        chosen_segments[label] = None
        actual_colors[label] = (0, 0, 0)
# === 라벨별 최종 선분 시각화 ===
for label, seg in chosen_segments.items():
    vis = cv2.cvtColor(resized_img, cv2.COLOR_GRAY2BGR)
    # 모든 Hough 선 회색으로
    for (x1,y1),(x2,y2) in segments:
        cv2.line(vis,(x1,y1),(x2,y2),(200,200,200),1)
    if seg:
        (x1,y1),(x2,y2) = seg
        cv2.line(vis,(x1,y1),(x2,y2),(0,0,255),2)
        cx,cy = label_positions[label]
        cv2.circle(vis,(cx,cy),5,(255,0,0),-1)
        cv2.putText(vis, label, (cx+5,cy-5), cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),1)
    cv2.imwrite(f"label_{label}_segment.png", vis)
    print(f"{label} segment 이미지 저장: label_{label}_segment.png")

# === 매핑 파일 갱신 ===
all_rows = []
with open("label_color_mapping.csv", "r", newline="", encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    header += ["Actual_R","Actual_G","Actual_B"]
    all_rows.append(header)
    for row in reader:
        lab = row[0]
        if lab in actual_colors:
            row += list(actual_colors[lab])
        else:
            row += ["","",""]
        all_rows.append(row)

with open("label_color_mapping.csv", "w", newline="", encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(all_rows)

print("라벨별 실제 색상 매핑이 완료되었습니다.")
