import cv2
import numpy as np
from PIL import Image
import io

def validate_image_file(file):
    """Validate uploaded image file"""
    # Check file size (max 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    file.seek(0, io.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    if size > MAX_FILE_SIZE:
        raise ValueError("File size too large. Maximum size is 10MB")

    # Check file type
    try:
        image = Image.open(file)
        if image.format not in ['JPEG', 'PNG', 'BMP']:
            raise ValueError("Invalid image format. Only JPEG, PNG and BMP are supported")
        
        # Check dimensions
        width, height = image.size
        if width < 100 or height < 100:
            raise ValueError("Image too small. Minimum dimensions are 100x100")
        if width > 5000 or height > 5000:
            raise ValueError("Image too large. Maximum dimensions are 5000x5000")
            
        # Convert to numpy array for additional checks
        img_np = np.array(image)
        
        # Check if image is too dark or too bright
        if img_np.mean() < 20:
            raise ValueError("Image too dark. Please use a better lit image")
        if img_np.mean() > 235:
            raise ValueError("Image too bright. Please use a better exposed image")
            
        return True
        
    except Exception as e:
        raise ValueError(f"Invalid image file: {str(e)}")

def validate_color_code(color_code):
    """Validate color code format"""
    import re
    
    # Supported formats:
    # H123, HL123, XF-12, X-12, TS-12
    patterns = [
        r'^H\d{1,4}$',
        r'^HL\d{1,4}$',
        r'^XF-\d{1,3}$',
        r'^X-\d{1,3}$',
        r'^TS-\d{1,3}$'
    ]
    
    if not any(re.match(pattern, color_code) for pattern in patterns):
        raise ValueError(f"Invalid color code format: {color_code}")
        
    return True
