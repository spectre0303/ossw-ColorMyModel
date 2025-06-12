import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import random
import colorsys

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

#<<<<<<이게 사용할 함수
def segment_and_colorize_ver1(img: Image.Image, num_regions: int = 5) -> Image.Image: 
    """
    이미지를 영역 분할하고 채색하여 파일로 저장하고 결과 경로 반환.

    Returns:
        dict: {
            "overlay": "path/to/2final_overlay.png"
        }
    """
    # === OCR, 전처리, 외곽선 추출, 필터링, 등 기존 코드 ===

    img_pil = img.convert("L")
    img_gray = np.array(img_pil)
    print("✅ img_gray.shape:", img_gray.shape)

    # 리사이즈
    h, w = img_gray.shape[:2]
    if h > 1800 or w > 1800:
        scale = 1800 / max(h, w)
        resized_img = cv2.resize(img_gray, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        img_gray = resized_img
    else:
        resized_img = img_gray

    # 윤곽선 추출 및 정제
    binary_adapt = cv2.adaptiveThreshold(resized_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 2)
    laplacian = cv2.Laplacian(binary_adapt, cv2.CV_8U, ksize=3)
    _, edge_mask = cv2.threshold(laplacian, 25, 255, cv2.THRESH_BINARY)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(edge_mask, 8)

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
    print("✅ quantized.shape:", quantized.shape)
    print("✅ external_mask.shape:", external_mask.shape)
    # === KMeans 분할
    # === 외곽 내부 영역만 추출 (원본 grayscale 기준)
    masked_pixels = quantized[external_mask == 255]
    print("✅ masked_pixels.shape:", masked_pixels.shape)
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

    return  Image.fromarray(cv2.cvtColor(blended, cv2.COLOR_BGR2RGB))
