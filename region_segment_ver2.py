import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import random
import colorsys

# ================= 색상 생성 함수 ===================
def generate_distinct_colors(n, sat_range=(0.4, 0.8), val_range=(0.6, 0.9)):
    """Generate visually distinct colors using HSV color space"""
    colors = []
    for i in range(n):
        # Use golden ratio to generate well-distributed hues
        hue = (i * 0.618033988749895) % 1.0
        # Randomize saturation and value within ranges for better distinction
        sat = np.random.uniform(sat_range[0], sat_range[1])
        val = np.random.uniform(val_range[0], val_range[1])
        # Convert HSV to RGB
        rgb = [int(x * 255) for x in colorsys.hsv_to_rgb(hue, sat, val)]
        colors.append(rgb)
    return colors

# ================= 메인 함수 ===================
def segment_and_colorize_ver2(pil_image: Image.Image, num_regions: int = 5) -> Image.Image:
    """Enhanced segmentation and colorization with improved edge detection"""
    img_pil = pil_image.convert("L")
    img_gray = np.array(img_pil)
    
    # Check resolution
    width, height = pil_image.size
    if (width >= height and (width < 1000 or height < 500)) or \
       (width < height and (width < 500 or height < 1000)):
        raise ValueError("Image resolution is too low")

    # Resize for processing
    h, w = img_gray.shape[:2]
    if h > 1800 or w > 1800:
        scale = 1800 / max(h, w)
        resized_img = cv2.resize(img_gray, (int(w * scale), int(h * scale)), 
                               interpolation=cv2.INTER_AREA)
    else:
        resized_img = img_gray

    # Edge detection with Canny
    blurred = cv2.GaussianBlur(resized_img, (3, 3), 0)
    edges = cv2.Canny(blurred, 50, 150)
    kernel = np.ones((3, 3), np.uint8)

    # Find contours
    contours_all, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Fill regions with average intensity
    avg_filled = resized_img.copy()
    for cnt in contours_all:
        for point in cnt:
            x, y = point[0]
            if 0 <= y < avg_filled.shape[0] and 0 <= x < avg_filled.shape[1]:
                # Use local average for better region consistency
                x0, x1 = max(x - 1, 0), min(x + 2, avg_filled.shape[1])
                y0, y1 = max(y - 1, 0), min(y + 2, avg_filled.shape[0])
                local_avg = int(np.mean(resized_img[y0:y1, x0:x1]))
                cv2.circle(avg_filled, (x, y), 1, local_avg, -1)

    # Quantize and create masked regions
    quantized = (avg_filled // 32) * 32
    lap_blur = cv2.GaussianBlur(quantized, (3, 3), 0)
    laplacian = cv2.Laplacian(lap_blur, cv2.CV_8U, ksize=3)
    _, edge_mask = cv2.threshold(laplacian, 25, 255, cv2.THRESH_BINARY)
    
    # Improve edge connectivity
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    edge_mask_closed = cv2.morphologyEx(edge_mask, cv2.MORPH_CLOSE, kernel)

    # Remove large edges iteratively
    image_area = resized_img.shape[0] * resized_img.shape[1]
    while True:
        contours_ext, _ = cv2.findContours(edge_mask_closed, 
                                         cv2.RETR_EXTERNAL, 
                                         cv2.CHAIN_APPROX_SIMPLE)
        found_large = False
        for cnt in contours_ext:
            if (cv2.contourArea(cnt) / image_area) >= 0.6:
                cv2.drawContours(edge_mask_closed, [cnt], -1, 0, 1)
                found_large = True
        if not found_large:
            break

    # Create final mask
    external_mask = np.zeros_like(edge_mask)
    contours_ext, _ = cv2.findContours(edge_mask_closed, 
                                     cv2.RETR_EXTERNAL, 
                                     cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours_ext:
        if cv2.contourArea(cnt) > 30:
            cv2.drawContours(external_mask, [cnt], -1, 255, -1)

    # Apply KMeans clustering
    masked_pixels = quantized[external_mask == 255]
    h, w = quantized.shape
    Z = masked_pixels.reshape((-1, 1)).astype(np.float32)
    kmeans = KMeans(n_clusters=num_regions, n_init=10)
    kmeans.fit(Z)

    # Create color image
    labels_full = np.full(quantized.shape, -1, dtype=np.int32)
    labels_full[external_mask == 255] = kmeans.labels_
    color_image = np.full((h, w, 3), 255, dtype=np.uint8)
    colors = generate_distinct_colors(num_regions)
    
    for i in range(num_regions):
        color_image[labels_full == i] = colors[i]

    # Apply median blur for smoother regions
    b, g, r = cv2.split(color_image)
    b_blur = cv2.medianBlur(b, 3)
    g_blur = cv2.medianBlur(g, 3)
    r_blur = cv2.medianBlur(r, 3)
    blurred_color_image = cv2.merge([b_blur, g_blur, r_blur])

    # Add edge overlay with transparency
    overlay = blurred_color_image.copy()
    edges = cv2.Canny(resized_img, 100, 200)
    overlay[edges == 255] = (0, 0, 0)
    alpha = 0.8
    blended = cv2.addWeighted(overlay, alpha, blurred_color_image, 1 - alpha, 0)

    return Image.fromarray(cv2.cvtColor(blended, cv2.COLOR_BGR2RGB))
