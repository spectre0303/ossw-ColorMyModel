import cv2                      # OpenCV: 이미지 처리, 윤곽선 추출, 블러, 필터 등 제공
import numpy as np              # NumPy: 이미지 배열 연산, 마스크 처리 등 수치 연산용
import pytesseract              # Tesseract OCR: 이미지에서 텍스트 추출

label_mode = 1  # 0: 숫자, 1: XF-X, X-X, TS-X, 2: H1-H9, 3: 문자형식
save_label_color_map = True
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

def sharpenImage(image):
    # Define a kernel for sharpening
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    
    # Apply the sharpening filter
    sharpened_image = cv2.filter2D(image, -1, kernel)
    
    return sharpened_image


def deskew(image):
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # Invert image: text should be white for moments
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Calculate image moments to estimate skew angle
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

def clearerText(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Denoise (helps reduce false contours)
    denoised = cv2.fastNlMeansDenoising(gray, h=20)

    # Apply Otsu's thresholding (black text on white background)
    _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Optional: Erode slightly to shrink wide characters and break merged strokes
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    cleaned = cv2.erode(binary, kernel, iterations=1)

    return cleaned

def getOCRText(image):
    # Use Tesseract to do OCR on the processed image
    custom_config = r'--oem 1 --psm 1'
    text = pytesseract.image_to_string(image, config=custom_config)
    return text

# Load the image
img_path = "Projects\Test_Img_12MP.jpg"
original_image = cv2.imread(img_path)

skewed_image = deskew(original_image)

# Apply the sharpening function
sharpened_image = sharpenImage(original_image)

# Apply the clearerText function
processed_image = clearerText(sharpened_image)

print(getOCRText(processed_image))

# Save or return the processed image
cv2.imwrite("./Projects/Processed_Test_Img_12MP.jpg", processed_image)
