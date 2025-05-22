import cv2
import pytesseract
import imutils

# tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

# Load the image
img = cv2.imread("Projects/Test_Img_12MP.jpg")  

#===============Image Preprocessing==========================

#gray scale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#thresholding with otsu (자동임계)
thersh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

# distance transform
dist = cv2.distanceTransform(thersh, cv2.DIST_L2, 5)
dist = cv2.normalize(dist, dist, 0, 1, cv2.NORM_MINMAX)
dist = (dist * 255).astype('uint8')
dsit = cv2.threshold(dist, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

# Morphological Operations
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
open = cv2.morphologyEx(dsit, cv2.MORPH_OPEN, kernel)           #opening
close = cv2.morphologyEx(open, cv2.MORPH_CLOSE, kernel)         #closing

#contours
cnts = cv2.findContours(close.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

nums = []
for c in cnts :
    (x, y, w, h) = cv2.boundingRect(c)
    if w >= 5 and w < 75 and h > 15 and h <= 35:
        nums.append(c)



#===============================================================