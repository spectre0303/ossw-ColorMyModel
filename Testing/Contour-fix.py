import cv2
import pytesseract
import numpy as np
from tqdm import tqdm
import re

# Field Settings
img_path = "Projects/Test_Img_12MP.jpg"  
custom_config = r'--oem 1 --psm 6'
languages = 'eng+jpn+chi_sim+chi_tra'
img = cv2.imread(img_path)

# Scaling the image by 2 times
scale_factor = 2
img = cv2.resize(img, (0, 0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)

# grayscale conversion
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# denoising
binary = cv2.fastNlMeansDenoising(gray, h=10)

# thresholding
binary = cv2.adaptiveThreshold(binary, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

# Getting Morphologiacal operations done
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
# opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
opened = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)      # may have to adjust this to enhance the outcome
#inverting the image for human checking
# opened = cv2.bitwise_not(opened)

cv2.imwrite("Projects/Scaled_Img.jpg", binary)

# OCR: Read and print lines using Tesseract
for _ in tqdm(range(1), desc="OCR Processing"):
    data = pytesseract.image_to_data(
        # cleaned
        opened, 
        lang=languages,
        config=custom_config,
        output_type=pytesseract.Output.DICT
    )

    n_boxes = len(data['level'])
    lines = {}
    for i in range(n_boxes):
        line_num = data['line_num'][i]
        text = data['text'][i].strip()
        if text:
            if line_num not in lines:
                lines[line_num] = []
            lines[line_num].append(text)

for line in sorted(lines.keys()):
    print(' '.join(lines[line]))

# print("=========================")
# text = pytesseract.image_to_string(opened, config=custom_config)
# print(text)

# print("=========================")

# pattern = r'H\s*\[?\s*(\d+)\s*\|\s*(\d+)\s*\]?'
# matches = re.findall(pattern, text)

# matches_ = re.findall(pattern, data)

# for match in matches:
#     print(f"H [{match[0]}|{match[1]}]")
#     # if no match is found, print a message
# if not matches:
#     print("No matches found. ++")

# for match in matches_:
#     print(f"H [{match[0]}|{match[1]}]")
#     # if no match is found, print a message
# if not matches_:
#     print("No matches found. __")

