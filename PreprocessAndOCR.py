import cv2
import easyocr
import re
import numpy as np

def process_1(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh

def process_2(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
    adaptive = cv2.adaptiveThreshold(
        bilateral, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 25, 10
    )
    return adaptive

def preprocess_image(image):
    h, w = image.shape[:2]
    mp = (h * w) / 1_000_000
    if 10 <= mp < 15:
        return process_1(image)
    elif 20 <= mp < 28:
        return process_2(image)
    else:
        return process_1(image)

def extract_code(texts):
    pattern = r'\b(H\d+|XF-\d+|X-\d+|TS-\d+)\b'
    codes = set()
    for t in texts:
        found = re.findall(pattern, t)
        codes.update(found)
    return list(codes)

def run_ocr_on_image(img_np):
    processed_img = preprocess_image(img_np)
    reader = easyocr.Reader(['en'])
    results = reader.readtext(processed_img, detail=1, paragraph=False)
    texts = [text for (_, text, _) in results]
    codes = extract_code(texts)
    return codes, texts

