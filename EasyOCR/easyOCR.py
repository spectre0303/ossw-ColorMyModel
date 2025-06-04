import easyocr
import cv2

# Load image
image_path = "Detected_Color_Codes_Output.jpg"
image = cv2.imread(image_path)

# Convert image to RGB
# image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.fastNlMeansDenoising(gray, h=20)

cv2.imwrite("Projects/Processed_Test_Img_12MP_thresh.jpg", gray)

# Initialize reader with English + Japanese
reader = easyocr.Reader(['en'])  # Add 'ch_sim' if you need Chinese too

# Run OCR
results = reader.readtext(image, detail=2, paragraph=False)

# Filter and print results
for (bbox, text, confidence) in results:
    if text.startswith('H'):
        print(f"Text: {text}, Confidence: {confidence}, Coordinates: {bbox}")