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
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # coords = np.column_stack(np.where(binary > 0))
    
    # if coords.shape[0] == 0:
    #     return image  # No foreground, return original

    # rect = cv2.minAreaRect(coords)
    # angle = rect[-1]
    # if angle < -45:
    #     angle = 90 + angle
    # else:
    #     angle = angle

    # # Only correct if angle is significant
    # if abs(angle) < 0.5:
    #     return image
    
    # (h, w) = image.shape[:2]
    # center = (w // 2, h // 2)
    # M = cv2.getRotationMatrix2D(center, angle, 1.0)
    # rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    rotated = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return rotated

# === Main OCR Routine ===
def preprocess_image(image):
    deskew(image)
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # _, thresh = cv2.threshold(gray,0,  255,
    #                                     cv2.THRESH_BINARY +
    #                                     cv2.THRESH_OTSU)

    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    # thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
    # kernel = np.ones((1, 1), np.uint8)
    # processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # return processed

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast = clahe.apply(gray)

    # Adaptive Threshold
    thresh = cv2.adaptiveThreshold(
        contrast, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV, 15, 10
    )

    # Morph close to fill gaps
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel)
    

    return morph


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
    color_code_pattern = re.compile(r"d{1,4}$", re.IGNORECASE)
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

    print(f"Found {len(extracted)} numeric codes.")
    for item in extracted:
        print(f"[{item['y']}] {item['text']} (conf={item['confidence']})")

if __name__ == "__main__":
    main("Projects\Image_test-2.jpg")