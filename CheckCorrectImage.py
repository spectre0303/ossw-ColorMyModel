import cv2
import numpy as np

def isfocused(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var > 100  # Adjust threshold as needed

def isblurry(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < 100  # Adjust threshold as needed

def isdark(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mean_intensity = gray.mean()
    return mean_intensity < 50  # Adjust threshold as needed

def isbright(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mean_intensity = gray.mean()
    return mean_intensity > 200  # Adjust threshold as needed

def islowcontrast(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    min_val, max_val = gray.min(), gray.max()
    return (max_val - min_val) < 50  # Adjust threshold as needed

# Real-time video capture
cap = cv2.VideoCapture(1)  # Use 1 for the external camera (adjust index if necessary)
# Automatically detect the camera index
# for i in range(2, 10000):  # Try indices from 0 to 9
#     test_cap = cv2.VideoCapture(i)
#     if test_cap.isOpened():
#         print(f"Camera found at index {i}")
#         cap = cv2.VideoCapture(i)
#         test_cap.release()
#         break
# else:
#     print("No camera found. Exiting...")
#     exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Check conditions
    focused = isfocused(frame)
    blurry = isblurry(frame)
    dark = isdark(frame)
    bright = isbright(frame)
    low_contrast = islowcontrast(frame)

    # Display results on the frame
    text = []
    if focused:
        text.append("Focused")
    if blurry:
        text.append("Blurry")
    if dark:
        text.append("Dark")
    if bright:
        text.append("Bright")
    if low_contrast:
        text.append("Low Contrast")

    for i, t in enumerate(text):
        cv2.putText(frame, t, (10, 30 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show the frame
    cv2.imshow("Real-Time Image Quality Check", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()