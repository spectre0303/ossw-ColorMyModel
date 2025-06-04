import cv2
import easyocr
import re

# Load grayscale image
image = cv2.imread("Projects\Processed_Test_Img_12MP.jpg", cv2.IMREAD_GRAYSCALE)

# Optional: apply Gaussian blur to reduce noise
blurred = cv2.GaussianBlur(image, (5, 5), 0)

# Initialize OCR reader
reader = easyocr.Reader(['en'])

# Define parameter ranges
block_sizes = [11, 15, 21, 25]
c_values = [0, 2, 5, 8, 10]

# Regex pattern: H followed by 2-4 digits (you can adjust this)
pattern = re.compile(r'H\d{1,6}')

results = []

for block_size in block_sizes:
    for c in c_values:
        # Must be odd and >=3
        if block_size % 2 == 0 or block_size < 3:
            continue

        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU,
            block_size, c
        )

        # Save or process thresholded image
        ocr_result = reader.readtext(thresh)

        # Extract only text strings
        words = [item[1] for item in ocr_result]

        # Count valid matches like H11, H317, etc.
        matches = [word for word in words if pattern.fullmatch(word)]
        match_count = len(matches)

        # Store result
        results.append({
            'block_size': block_size,
            'C': c,
            'matches': matches,
            'count': match_count
        })

        print(f"blockSize={block_size}, C={c}, Matches={match_count}: {matches}")

# Sort by best match count
results.sort(key=lambda x: x['count'], reverse=True)

# Display best result
best = results[0]
print("\n🎯 Best Parameters:")
print(f"blockSize={best['block_size']}, C={best['C']}")
print(f"Matches ({best['count']}): {best['matches']}")
