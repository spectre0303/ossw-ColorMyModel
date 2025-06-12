import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import random
import colorsys

# ================= 색상 생성 함수 ===================
def generate_distinct_colors(n, sat_range=(0.4, 0.8), val_range=(0.6, 0.9)):
    colors = set()
    max_attempts = 1000
    attempts, i = 0, 0

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
            attempts += 1
    return list(colors)

# ================= 메인 함수 ===================
def segment_and_colorize_ver2(pil_image: Image.Image, num_regions: int = 5) -> Image.Image:
    img_pil = pil_image.convert("L")
    img_gray = np.array(img_pil)
    print("✅ img_gray.shape:", img_gray.shape)

    # 크기 조정
    h, w = img_gray.shape[:2]
    if h > 1800 or w > 1800:
        scale = 1800 / max(h, w)
        resized_img = cv2.resize(img_gray, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        img_gray = resized_img
    else:
        resized_img = img_gray

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
    print("✅ quantized.shape:", quantized.shape)
    print("✅ external_mask.shape:", external_mask.shape)
    ##===============================외곽 윤곽선 끝

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
    b, g, r = cv2.split(color_image)
    b_blur = cv2.medianBlur(b, 3)
    g_blur = cv2.medianBlur(g, 3)
    r_blur = cv2.medianBlur(r, 3)
    blurred_color_image = cv2.merge([b_blur, g_blur, r_blur])

    #윤곽선을 thinned로 투명도 80퍼센트로 그리기
    overlay = blurred_color_image.copy()
    overlay[edges == 255] = (0, 0, 0)
    alpha = 0.8
    blended = cv2.addWeighted(overlay, alpha, blurred_color_image, 1 - alpha, 0)

    # PIL Image로 반환
    return Image.fromarray(cv2.cvtColor(blended, cv2.COLOR_BGR2RGB))
