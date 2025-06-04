import cv2
import easyocr
import re

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Adaptive thresholding helps with lighting and font clarity
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )
    return thresh

def detect_color_code_boxes(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # step 1 : Adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV, 15, 10
    )

    # Step 2: Use morphological operations to isolate horizontal boxes
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 20))  # horizontal emphasis
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Step 3: Find external contours
    contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if 60 < w < 400 and 20 < h < 80:  # tuned for H codes
            boxes.append((x, y, w, h))
            
    return boxes

def extract_code(image, box, reader):
    x, y, w, h = box
    roi = image[y:y+h, x:x+w]
    
    roi = cv2.resize(roi, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)  # Upscale ROI
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, roi_bin = cv2.threshold(roi_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    cv2.imwrite(f"Projects/ossw-ColorMyModel/RoiTest/box_debug_{x}_{y}.png", roi_bin)
    # easyocr expects RGB images
    roi_rgb = cv2.cvtColor(roi_bin, cv2.COLOR_GRAY2RGB)
    result = reader.readtext(roi_rgb, detail=0)
    raw_text = " ".join(result)
    
    # Clean up and match codes
    match = re.search(r'H\s*\d{1,3}', raw_text)
    if match:
        return match.group(0).replace(" ", "")
    return ""

def main(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print("Image not found.")
        return

    reader = easyocr.Reader(['en'], gpu=False)
    boxes = detect_color_code_boxes(image)
    print(f"Found {len(boxes)} candidate boxes.")

    results = set()
    for box in boxes:
        code = extract_code(image, box, reader)
        if code.startswith("H") and len(code) >= 2:
            results.add(code)
            # Optional: draw box
            x, y, w, h = box
            cv2.rectangle(image, (x, y), (x+w, y+h), (0,255,0), 2)
            cv2.putText(image, code, (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)

    if results:
        print("Detected color codes:")
        for r in sorted(results, key=lambda x: int(x[1:])):
            print(r)
    else:
        print("No valid color codes found.")
    
    # cv2.imshow("Detected Codes", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

if __name__ == "__main__":
    main("Projects/Test_Img_12MP.jpg")
