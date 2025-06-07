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

def check_image_quality(frame):
    
    return {
        "focused": isfocused(frame),
        "blurry": isblurry(frame),
        "dark": isdark(frame),
        "bright": isbright(frame),
        "low_contrast": islowcontrast(frame)
    }