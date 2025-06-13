import cv2

def isfocused(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var > 100

def isblurry(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < 100

def isdark(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mean_intensity = gray.mean()
    return mean_intensity < 50

def isbright(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mean_intensity = gray.mean()
    return mean_intensity > 300

def islowcontrast(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    min_val, max_val = gray.min(), gray.max()
    return (max_val - min_val) < 50

def isSmall(frame):
    height, width = frame.shape[:2]
    if width >= height:
        return (width < 1000 or height < 500)
    else:
        return (width < 500 or height < 1000)

def analyze_image_quality(frame):
    """
    이미지의 품질을 분석하고 문제점 설명 리스트 또는 None 반환

    Returns:
        None if image is only focused and no issues,
        list of strings describing issues otherwise.
    """
    results = []

    focused = isfocused(frame)
    blurry = isblurry(frame)
    dark = isdark(frame)
    bright = isbright(frame)
    low_contrast = islowcontrast(frame)
    small = isSmall(frame)

    # 조건들에 따라 메시지 저장
    if blurry:
        results.append("이미지가 흐립니다.")
    if dark:
        results.append("이미지가 너무 어둡습니다.")
    if bright:
        results.append("이미지가 너무 밝습니다.")
    if low_contrast:
        results.append("대비가 너무 낮습니다.")
    if small:
        results.append("이미지 해상도가 너무 낮습니다.")

    # 만약 다른 건 다 false고 focused만 true면 → None 반환
    if focused and not results:
        return None

    return results
