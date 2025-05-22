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
def preprocess_image(image):
    # skew the image
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # sharpen the image
    kernel = np.array([[0, -1, 0], 
                       [-1, 5, -1], 
                       [0, -1, 0]])
    sharpened = cv2.filter2D(image, -1, kernel)
    


def preprocess_and_segment(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Inverted thresholding to catch both black-on-white and white-on-black
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find external contours (boxes around characters)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = [cv2.boundingRect(c) for c in contours if cv2.contourArea(c) > 50]
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
