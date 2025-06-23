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
    """Enhanced code extraction with improved pattern matching"""
    patterns = [
        r'\b(H\d+)',           # H followed by numbers
        r'\b(XF-\d+)',         # XF- followed by numbers
        r'\b(X-\d+)',          # X- followed by numbers
        r'\b(TS-\d+)',         # TS- followed by numbers
        r'\b(H[A-Z]\d+)',      # H followed by letter and numbers
        r'\b(XF[A-Z]\d+)',     # XF followed by letter and numbers
        r'\b(H[L]?-?\d{1,6})', # Handle variations like HL1162
        r'\b([A-Z]\d{1,3})'    # Generic letter-number combinations
    ]
    
    codes = set()
    for t in texts:
        # Cleanup: remove spaces and normalize
        t = re.sub(r'\s+', '', t.upper())
        for pattern in patterns:
            found = re.findall(pattern, t, re.IGNORECASE)
            codes.update(found)
    
    return sorted(list(codes), key=lambda x: (x[0], int(re.search(r'\d+', x).group())))

def enhanced_preprocess(image):
    """Enhanced preprocessing pipeline combining multiple techniques"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply CLAHE for better contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_img = clahe.apply(gray)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(clahe_img, h=10)
    
    # Sharpen
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(denoised, -1, kernel)
    
    # Final threshold with morphological operations
    thresh = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel)
    
    return morph

def run_ocr_on_image(img_np):
    """Enhanced OCR with better error handling and validation"""
    try:
        # Validate input
        if img_np is None or not isinstance(img_np, np.ndarray):
            raise ValueError("Invalid input image")
            
        # Check image dimensions
        if len(img_np.shape) != 3:
            raise ValueError("Image must be a 3-channel color image")
            
        # Process image
        processed_img = enhanced_preprocess(img_np)
        
        # Initialize reader with confidence threshold
        reader = easyocr.Reader(['en', 'ja'], gpu=True)  # Added Japanese support
        results = reader.readtext(processed_img, 
                                detail=1, 
                                paragraph=False,
                                min_size=10,
                                contrast_ths=0.1,
                                adjust_contrast=0.5,
                                text_threshold=0.7)
        
        texts = [text for (_, text, conf) in results if conf > 0.5]  # Filter by confidence
        codes = extract_code(texts)
        
        return codes, texts
        
    except Exception as e:
        print(f"Error in OCR processing: {str(e)}")
        return [], []
