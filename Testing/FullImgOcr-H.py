import cv2
import easyocr
import numpy as np
import re
import json

# === Parameters ===
CONFIDENCE_THRESHOLD = 0.2
RESIZE_WIDTH = 2000   # Resize width for better recognition
DEBUG_SAVE = True

# === Text Cleaning ===
def clean_text(text):
    return re.sub(r"[^A-Z0-9\-]", "", text.strip().upper())

# === Deskewing Function ===
def deskew(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(binary > 0))
    
    if coords.shape[0] == 0:
        return image  # No foreground, return original

    rect = cv2.minAreaRect(coords)
    angle = rect[-1]
    if angle < -45:
        angle = 90 + angle
    else:
        angle = angle

    # Only correct if angle is significant
    if abs(angle) < 0.5:
        return image
    
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated

# === Main OCR Routine ===
def preprocess_image(image):
    # 1. Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.fastNlMeansDenoising(gray, h=10)

    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    gray = cv2.filter2D(gray, -1, kernel)


    # 2. Adaptive thresholding (combine with OTSU)
    # Try adaptive first, fallback to OTSU if needed
    adaptive = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 31, 15
    )
    otsu = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    # Heuristic: Use the one with more white pixels (less noise)
    if np.sum(adaptive == 255) > np.sum(otsu == 255):
        thresh = adaptive
    else:
        thresh = otsu

    #sharpen image

    # 3. Morphological operations (open to remove noise, close to connect text)
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    # opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    # closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel, iterations=1)

    # 4. Optionally resize for better OCR
    # h, w = closed.shape
    # if w < RESIZE_WIDTH:
    #     scale = RESIZE_WIDTH / w
    #     closed = cv2.resize(closed, (RESIZE_WIDTH, int(h * scale)), interpolation=cv2.INTER_CUBIC)

    # return closed

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    return cleaned


def clean_text(text):
    # Remove spaces and dashes, uppercase
    return re.sub(r"[^A-Z0-9]", "", text.strip().upper())

def main(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print("Image not found.")
        return

    processed = preprocess_image(image)
    reader = easyocr.Reader(['en', 'ja'], gpu=True)  # Use GPU and Japanese
    results = reader.readtext(processed)

    results.sort(key=lambda r: r[0][0][1]) 
    extracted = []

    # Regex for color codes like H11, H317, H327, etc.
    color_code_pattern = re.compile(r"^H[L]?-?\d{1,6}$", re.IGNORECASE)
    # color_code_pattern = re.compile(r"^H[L]?-?\d{1,4}$", re.IGNORECASE)
    
    for bbox, text, conf in results:
        cleaned = clean_text(text)
        if conf >= 0.0 and color_code_pattern.match(cleaned):
            extracted.append({
                "text": cleaned,
                "confidence": round(float(conf), 3),
                "y": int(bbox[0][1]),
                "bbox": [(int(x), int(y)) for (x, y) in bbox]
            })
            if DEBUG_SAVE:
                cv2.rectangle(processed, tuple(map(int, bbox[0])), tuple(map(int, bbox[2])), (0, 255, 0), 2)
                cv2.putText(processed, cleaned, tuple(map(int, bbox[0])), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    if DEBUG_SAVE:
        cv2.imwrite("debug_output.jpg", processed)

    with open("extracted_color_codes.json", "w", encoding="utf-8") as f:
        json.dump(extracted, f, indent=2, ensure_ascii=False)

    print(f"Found {len(extracted)} color codes starting with 'H'.")
    for item in extracted:
        print(f"[{item['y']}] {item['text']} (conf={item['confidence']})")

def extract_all_text(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print("Image not found.")
        return []

    processed = preprocess_image(image)
    reader = easyocr.Reader(['en'], gpu=True)
    results = reader.readtext(processed)

    extracted = []
    for bbox, text, conf in results:
        cleaned = re.sub(r"[^A-Z0-9]", "", text.strip().upper())
        if cleaned:  # Only keep non-empty results
            extracted.append({
                "text": cleaned,
                "confidence": round(float(conf), 3),
                "y": int(bbox[0][1]),
                "bbox": [(int(x), int(y)) for (x, y) in bbox]
            })
            print(f"[{int(bbox[0][1])}] {cleaned} (conf={round(float(conf), 3)})")
            cv2.rectangle(processed, tuple(map(int, bbox[0])), tuple(map(int, bbox[2])), (0, 255, 0), 2)
            cv2.putText(
                processed,
                cleaned,
                (int(bbox[0][0]), int(bbox[0][1]) - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),  # Green color for text
                2
            )
            # Convert processed (grayscale) back to color for visualization
            if len(processed.shape) == 2:
                processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
            cv2.imwrite("debug_output_all_text.jpg", processed)
    return extracted

if __name__ == "__main__":
    main("Projects\Test_Img_12MP.jpg")
    print("=======================")
    extract_all_text("Projects\Test_Img_12MP.jpg")