import easyocr
import cv2
import numpy as np
import re

# Routine 1 : Denoise + OTSU
def process_1(image) :
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh

# Routine 2 : Sharpen + CLAHE + OTSU
def process_2(image) :
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(gray, -1, kernel)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_image = clahe.apply(sharpened)
    
    thresh = cv2.threshold(clahe_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh

# Routine 3 : CLAHE + DENOISE + ADAPTIVE + Morph Open
def process_3(image) :
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_image = clahe.apply(gray)
    
    denoised = cv2.fastNlMeansDenoising(clahe_image, h=10)
    
    adaptive_thresh = cv2.adaptiveThreshold(
        denoised, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 25, 2
    )
    
    kernel = np.ones((3, 3), np.uint8)
    morph_opened = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_OPEN, kernel)
    
    return morph_opened

# Routine 4 : Sharpen + ClAHE + OTSU
def process_4(image) :
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(gray, -1, kernel)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_image = clahe.apply(sharpened)
    
    thresh = cv2.threshold(clahe_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh


# Routine 5 : Histogram Equalization + OTSU + Morph Close
def process_5(image) :
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hist_eq = cv2.equalizeHist(gray)
    
    thresh = cv2.threshold(hist_eq, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    kernel = np.ones((3, 3), np.uint8)
    morph_closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    return morph_closed


# Routine 6 : Bilateral Filter + Adaptive Threshold
def process_6(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
    adaptive = cv2.adaptiveThreshold(
        bilateral, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 25, 10
    )
    return adaptive

# Routine 7 : Top-hat Morphology + CLAHE + OTSU
def process_7(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_img = clahe.apply(tophat)
    thresh = cv2.threshold(clahe_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh

# Routine 8: Median Blur + Adaptive Threshold + Morph Close
def process_8(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    median = cv2.medianBlur(gray, 3)
    adaptive = cv2.adaptiveThreshold(
        median, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 17, 3
    )
    kernel = np.ones((2, 2), np.uint8)
    closed = cv2.morphologyEx(adaptive, cv2.MORPH_CLOSE, kernel)
    return closed

# Routine 9 : sobel Edge + OTSU
def process_9(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sobel = cv2.Sobel(gray, cv2.CV_8U, 1, 0, ksize=3)
    thresh = cv2.threshold(sobel, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh


#Routine 10: Invert + CLAHE + OTSU
def process_10(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    inv = cv2.bitwise_not(gray)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_img = clahe.apply(inv)
    thresh = cv2.threshold(clahe_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh




Routines = [process_1, process_2, process_3, process_4, process_5, process_6, process_7, process_8, process_9, process_10]       

for i, routine in enumerate(Routines):
    print(f"Running Routine {i+1}...")
    
    # Load image
    image = cv2.imread("Projects/Processed_Test_Img_12MP.jpg")
    
    # Process image
    processed_image = routine(image)
    
    # Initialize OCR reader
    reader = easyocr.Reader(['en'])
    
    # Perform OCR
    ocr_result = reader.readtext(processed_image)
    
    # Extract only text strings
    # Extract only text strings that start with 'H'
    words = [item[1] for item in ocr_result if isinstance(item[1], str) and item[1].startswith('H')]

    # Draw boxes around detected texts that start with 'H'
    boxed_image = image.copy()
    for bbox, text, conf in ocr_result:
        if isinstance(text, str) and text.startswith('H'):
            pts = np.array(bbox, dtype=np.int32)
            cv2.polylines(boxed_image, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
            cv2.putText(boxed_image, text, tuple(pts[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    cv2.imwrite(f"Projects/ossw-ColorMyModel/EasyOCR/Routines/routine_{i+1}_boxed.jpg", boxed_image)
    
    # Print results
    print(f"Routine {i+1} Results: {words}")