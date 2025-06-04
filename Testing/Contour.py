import cv2
import pytesseract
from collections import defaultdict
import numpy as np

# Path to your image
image_path = "Projects/Test_Img_12MP.jpg"  # replace with your actual image filename

# Configuration for Tesseract
custom_config = r'--oem 1 --psm 6 -c tessedit_char_whitelist=0123456789H'

# ==================Image Preprocessing Function==========================
# This function will preprocess the image to make it suitable for OCR
def deskew(image):
    # deskew the image
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

def preprocess_image(image):
    image = deskew(image)

    # denoise the image
    denoised = cv2.fastNlMeansDenoising(image, h=20)

    # morphological operations to clean up the image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    cleaned = cv2.erode(denoised, kernel, iterations=1)
    cleaned = cv2.dilate(cleaned, kernel, iterations=1)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)

    # sharpen the image
    kernel = np.array([[0, -1, 0], 
                       [-1, 5, -1], 
                       [0, -1, 0]])
    sharpened = cv2.filter2D(cleaned, -1, kernel)

    resized = cv2.resize(sharpened, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    return resized


def preprocess_and_segment(image_path):
    img = preprocess_image(cv2.imread(image_path))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Inverted thresholding to catch both black-on-white and white-on-black
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find external contours (boxes around characters)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = [cv2.boundingRect(c) for c in contours if cv2.contourArea(c) > 25] 
    boxes = sorted(boxes, key=lambda b: (b[1], b[0]))  # sort top to bottom, left to right

    results = []
    for (x, y, w, h) in boxes:
        char_img = gray[y:y+h, x:x+w]

        # Try both normal and inverted thresholds
        _, normal = cv2.threshold(char_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        _, inverted = cv2.threshold(char_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        text_norm = pytesseract.image_to_string(normal, config=custom_config).strip()
        text_inv = pytesseract.image_to_string(inverted, config=custom_config).strip()

        best_text = text_norm if len(text_norm) >= len(text_inv) else text_inv
        results.append((x, y, best_text))

    return results

def group_lines(results, line_threshold=20):
    lines = defaultdict(list)

    for x, y, char in results:
        matched = False
        for key in lines:
            if abs(y - key) < line_threshold:
                lines[key].append((x, char))
                matched = True
                break
        if not matched:
            lines[y].append((x, char))

    final_lines = []
    for key in sorted(lines):
        line = sorted(lines[key], key=lambda c: c[0])
        final_lines.append(''.join([c[1] for c in line]))
    return final_lines

# Run everything
char_results = preprocess_and_segment(image_path)
lines = group_lines(char_results)

# Output
print("📝 Extracted Lines:")
for line in lines:
    print(line)
