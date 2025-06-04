import cv2
import numpy as np
from PIL import Image
import pytesseract
import re
import csv

pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

def load_image(image_path):
    return cv2.imread(image_path)

image_path = "Projects/Test_Img_12MP.jpg"  # Replace with your image path

def parse_text_from_image(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    extracted_text = pytesseract.image_to_string(gray_image, config='--psm 6')

    return extracted_text

# Function to process extracted text with custom conditions and prefixes
def process_text(extracted_text, conditions_and_prefixes):
    """
    Processes the extracted text by applying conditions and adding prefixes.
    
    Args:
        extracted_text (str): Text extracted from the image.
        conditions_and_prefixes (list of tuples): Each tuple contains a condition (callable) 
                                                  and a prefix (str) to apply if the condition is met.
    
    Returns:
        list of str: Processed lines of text.
    """
    processed_lines = []
    lines = extracted_text.splitlines()
    
    for line in lines:
        line = line.strip()
        if not line:  # Skip empty lines
            continue
        
        for condition, prefix in conditions_and_prefixes:
            if condition(line):  # Check if the condition is met
                line = f"{prefix}{line}"  # Add the prefix
                break  # Stop checking other conditions for this line
        
        processed_lines.append(line)
    
    return processed_lines

# Example usage structure
if __name__ == "__main__":
    # Load the image
    image_path = "Projects\Test_Img_12MP.jpg"  # Replace with your image path
    image = load_image(image_path)
    
    # Parse text from the image
    extracted_text = parse_text_from_image(image)
    
    # Define conditions and prefixes
    # Example: Add "PREFIX: " to lines containing the word "example"
    conditions_and_prefixes = [
        (lambda line: "example" in line.lower(), "PREFIX: "),
        (lambda line: line.isdigit(), "NUMBER: "),
    ]
    
    # Process the extracted text
    processed_text = process_text(extracted_text, conditions_and_prefixes)
    
    # Print the processed text
    for line in processed_text:
        print(line)