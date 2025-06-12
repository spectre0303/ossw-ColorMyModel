from flask import Flask, request, jsonify, send_file
from region_segment_ver1 import segment_and_colorize_ver1
from region_segment_ver2 import segment_and_colorize_ver2
from flask_cors import CORS
from PIL import Image, ImageOps
import io
import base64
import numpy as np
from PreprocessAndOCR import run_ocr_on_image

app = Flask(__name__)
CORS(app)  # 모든 도메인에 대해 CORS 허용

click_counts = {}

@app.route('/upload', methods=['POST'])
def upload_image():
    file = request.files['image']
    client_ip = request.remote_addr

    print(f"요청 받음 - 클라이언트 IP: {client_ip}")
    print(f"업로드된 파일 이름: {file.filename}")

    try:
        count = click_counts.get(client_ip, 0) + 1
        click_counts[client_ip] = count

        # OCR 수행
        img_ocr = Image.open(file.stream).convert("RGB")
        img_np = np.array(img_ocr)
        print(f"[OCR 요청] 클라이언트 IP: {client_ip}, 이미지 shape: {img_np.shape}")

        codes, texts = run_ocr_on_image(img_np)
        print(f"인식된 코드들: {codes}")
        print(f"인식된 텍스트들: {texts}")

        img = Image.open(file.stream)

        # 이미지 2개 생성
        result1 = segment_and_colorize_ver1(img)
        result2 = segment_and_colorize_ver2(img)

        def image_to_base64(image_obj):
            img_io = io.BytesIO()
            image_obj.save(img_io, format='PNG')
            img_io.seek(0)
            return base64.b64encode(img_io.read()).decode('utf-8')
        
        grayscale_b64 = image_to_base64(result1)
        inverted_b64 = image_to_base64(result2)

        print("OCR 데이터 및 이미지 2개 전송 준비 완료")
        return jsonify({
            'grayscale': grayscale_b64,
            'inverted': inverted_b64,
            'codes': codes,
            'texts': texts
        })

    except Exception as e:
        print(f"error in processing image: {e}")
        return "image process failed", 500

from PIL import ImageDraw, ImageShow  # ImageDraw도 import 필요


@app.route('/color_point', methods=['POST'])
def color_point():
    client_ip = request.remote_addr
    count = click_counts.get(client_ip, 0) + 1
    click_counts[client_ip] = count

    data = request.form.get('data')
    if not data:
        return "Bad Request: JSON data (form-data 'data') required", 400

    try:
        data_json = json.loads(data)
    except Exception as e:
        return f"Bad Request: JSON parsing error: {e}", 400

    x = data_json.get('x')
    y = data_json.get('y')
    color = data_json.get('color')

    if x is None or y is None or color is None:
        return "Bad Request: x, y, color fields required", 400

    try:
        x = int(float(x))
        y = int(float(y))
    except ValueError:
        return "Bad Request: x and y must be numeric", 400

    print(f"[좌표 클릭] 클라이언트 IP: {client_ip}, x={x}, y={y}, color={color}")
    print(f"{client_ip}의 현재 클릭 횟수: {count}")

    file = request.files.get('image')
    if not file:
        return "Bad Request: Image file required", 400

    try:
        img = Image.open(file.stream).convert("RGB")
        img_np = np.array(img)
        print("원본 이미지 shape:", img_np.shape)

        clicked_color = img_np[y, x]  # y 먼저!
        print(f"📍 클릭한 좌표의 실제 색: {clicked_color}")

        # 기준 색상과의 차이가 일정 이하인 픽셀만 선택
        threshold = 40  # 색 차이 허용 범위
        diff = np.linalg.norm(img_np - clicked_color, axis=2)
        mask = diff < threshold

        # 선택된 색상 값
        color_map = {
            'RED': (255, 0, 0),
            'GREEN': (0, 255, 0),
            'BLUE': (0, 0, 255),
            'PURPLE': (128, 0, 128),
            'TS-1' : (112, 66, 65),
            'TS-2' : (54, 69, 59),
            'TS-3' : (160, 143, 89),
            'TS-4' : (64, 64, 64),
            'TS-5' : (83, 86, 65),
            'TS-6' : (0, 0, 0),
            'TS-7' : (255, 255, 255),
            'TS-8' : (186, 0, 0),
            'TS-9' : (0, 64, 0),
            'TS-10' : (0, 0, 255),
            'TS-11' : (128, 0, 0),
            'TS-12' : (255, 102, 0),
            'TS-14' : (0, 0, 0),
            'TS-15' : (0, 0, 139),
            'TS-16' : (255, 255, 0),
            'TS-17' : (192, 192, 192),
            'TS-18' : (178, 34, 34),
            'TS-19' : (0, 0, 205),
            'TS-20' : (0, 128, 0),
            'TS-21' : (255, 215, 0),
            'TS-22' : (144, 238, 144),
            'TS-23' : (173, 216, 230),
            'TS-24' : (128, 0, 128),
            'TS-25' : (255, 192, 203),
            'TS-26' : (255, 255, 255),
            'TS-27' : (255, 255, 255),
            'TS-28' : (107, 142, 35),
            'TS-29' : (33, 33, 33),
            'TS-30' : (192, 192, 192),
            'TS-31' : (255, 165, 0),
            'TS-32' : (169, 169, 169),
            'TS-33' : (139, 0, 0),
            'TS-34' : (193, 154, 107),
            'TS-35' : (0, 128, 0),
            'TS-36' : (255, 36, 0),
            'TS-37' : (230, 230, 250),
            'TS-38' : (42, 42, 42),
            'TS-39' : (178, 34, 34),
            'TS-40' : (33, 33, 33),
            'TS-41' : (0, 255, 255),
            'TS-42'  : (169, 169, 169),
            'TS-43' : (0, 100, 0),
            'TS-44' : (0, 0, 255),
            'TS-45' : (255, 255, 255),
            'TS-46' : (244, 164, 96),
            'TS-47' : (255, 215, 0),
            'TS-48' : (47, 79, 79),
            'TS-49' : (255, 0, 0),
            'TS-50' : (0, 0, 205),
            'TS-51' : (0, 0, 255),
            'TS-52' : (50, 205, 50),
            'TS-53' : (0, 0, 139),
            'TS-54' : (173, 216, 230),
            'TS-55' : (0, 0, 139),
            'TS-56' : (255, 165, 0),
            'TS-57' : (138, 43, 226),
            'TS-58' : (173, 216, 230),
            'TS-59' : (255, 182, 193),
            'TS-60' : (144, 238, 144),
            'TS-61' : (85, 107, 47),
            'TS-62' : (139, 69, 19),
            'TS-63' : (0, 0, 0),
            'TS-64' : (0, 0, 139),
            'TS-66' : (169, 169, 169),
            'TS-67' : (169, 169, 169),
            'TS-68' : (210, 180, 140),
            'TS-69' : (139, 69, 19),
            'TS-70' : (107, 142, 35),
            'TS-71' : (105, 105, 105),
            'TS-72' : (0, 0, 255),
            'TS-73' : (255, 165, 0),
            'TS-74' : (255, 0, 0),
            'TS-75' : (250, 214, 165),
            'TS-76' : (192, 192, 192),
            'TS-77' : (255, 224, 189),
            'TS-78' : (128, 128, 128),
            'TS-81'  : (211, 211, 211),
            'TS-82' : (33, 33, 33),
            'TS-83' : (192, 192, 192),
            'TS-84' : (255, 215, 0),
            'TS-85' : (178, 34, 34),
            'TS-86' : (255, 0, 0),
            'TS-87' : (255, 215, 0),
            'TS-88' : (192, 192, 192),
            'TS-89' : (173, 216, 230),
            'TS-90' : (139, 69, 19),
            'TS-91' : (0, 100, 0),
            'TS-92' : (255, 140, 0),
            'TS-93' : (0, 0, 255),
            'TS-94' : (169, 169, 169),
            'TS-95' : (178, 34, 34),
            'TS-96' : (255, 69, 0),
            'TS-97' : (255, 255, 0),
            'TS-98' : (255, 165, 0),
            'TS-99' : (169, 169, 169),
            'TS-100' : (105, 105, 105),
            'TS-101' : (255, 255, 255),
            'TS-102' : (0, 255, 255),
            'X-1' : (0, 0, 0),
            'X-2' : (255, 255, 255),
            'X-3' : (0, 0, 255),
            'X-4' : (0, 0, 139),
            'X-5' : (0, 128, 0),
            'X-6' : (255, 165, 0),
            'X-7' : (255, 0, 0),
            'X-8' : (255, 250, 205),
            'X-9' : (139, 69, 19),
            'X-10' : (42, 42, 42),
            'X-11' : (192, 192, 192),
            'X-12' : (255, 215, 0),
            'X-13' : (0, 0, 205),
            'X-14' : (135, 206, 235),
            'X-15' : (144, 238, 144),
            'X-16' : (128, 0, 128),
            'X-17' : (255, 192, 203),
            'X-18' : (33, 33, 33),
            'X-19' : (105, 105, 105),
            'X-23' : (0, 0, 139),
            'X-24' : (255, 250, 205),
            'X-25' : (0, 128, 0),
            'X-26' : (255, 165, 0),
            'X-27' : (255, 0, 0),
            'X-28' : (0, 128, 0),
            'X-30' : (255, 250, 205),
            'X-31' : (255, 215, 0),
            'X-32' : (192, 192, 192),
            'X-33' : (205, 127, 50),
            'X-34' : (153, 62, 5),
            'XF-1' : (0, 0, 0),
            'XF-2' : (255, 255, 255),
            'XF-3' : (255, 215, 0),
            'XF-4' : (154, 205, 50),
            'XF-5' : (0, 100, 0),
            'XF-6' : (184, 115, 51),
            'XF-7' : (139, 0, 0),
            'XF-8' : (0, 0, 139),
            'XF-9' : (128, 0, 0),
            'XF-10' : (139, 69, 19),
            'XF-11' : (60, 179, 113),
            'XF-12' : (169, 169, 169),
            'XF-13' : (34, 139, 34),
            'XF-14' : (176, 196, 222),
            'XF-15' : (255, 228, 196),
            'XF-16' : (211, 211, 211),
            'XF-17' : (70, 130, 180),
            'XF-18' : (0, 0, 205),
            'XF-19' : (176, 196, 222),
            'XF-20' : (169, 169, 169),
            'XF-21' : (135, 206, 235),
            'XF-22' : (128, 128, 128),
            'XF-23' : (173, 216, 230),
            'XF-24' : (169, 169, 169),
            'XF-25' : (176, 196, 222),
            'XF-26' : (0, 100, 0),
            'XF-27' : (1, 50, 32),
            'XF-28' : (139, 64, 0),
            'XF-49' : (240, 230, 140),
            'XF-50' : (65, 105, 225),
            'XF-51' : (107, 142, 35),
            'XF-52' : (139, 69, 19),
            'XF-53' : (128, 128, 128),
            'XF-54' : (139, 139, 131),
            'XF-55' : (210, 180, 140),
            'XF-56' : (169, 169, 169),
            'XF-57' : (245, 222, 179),
            'XF-58' : (128, 128, 0),
            'XF-59' : (237, 201, 175),
            'XF-60' : (189, 183, 107),
            'XF-61' : (0, 100, 0),
            'XF-62' : (107, 142, 35),
            'XF-63' : (75, 75, 75),
            'XF-64' : (165, 42, 42),
            'XF-65' : (85, 107, 47),
            'XF-66' : (211, 211, 211),
            'XF-67' : (75, 83, 32),
            'XF-68' : (139, 69, 19),
            'XF-69' : (0, 0, 0),
            'XF-70' : (0, 100, 0),
            'XF-71' : (60, 179, 113),
            'XF-72' : (139, 69, 19),
            'XF-73' : (0, 100, 0),
            'XF-74' : (107, 142, 35),
            'XF-75' : (169, 169, 169),
            'XF-76' : (176, 196, 222),
            'XF-77' : (169, 169, 169),
            'XF-78' : (222, 184, 135),
            'XF-79' : (139, 69, 19),
            'XF-80' : (211, 211, 211),
            'XF-81' : (0, 100, 0),
            'XF-82' : (169, 169, 169),
            'XF-83' : (176, 196, 222),
            'XF-84' : (63, 63, 63),
            'XF-85' : (47, 79, 79),
            'XF-87' : (169, 169, 169),
            'XF-88' : (189, 183, 107),
            'XF-89' : (0, 100, 0),
            'XF-90' : (165, 42, 42),
            'XF-91' : (169, 169, 169),
            'XF-92' : (237, 201, 175),
            'XF-93' : (229, 179, 110),
        }
        target_color = np.array(color_map.get(color.upper(), (255, 255, 255)))

        # mask가 True인 부분만 색 변경
        result_np = img_np.copy()
        result_np[mask] = target_color

        result_img = Image.fromarray(result_np)
        img_io = io.BytesIO()
        result_img.save(img_io, 'PNG')
        img_io.seek(0)

        print("✅ 색상 변경된 이미지 반환")
        return send_file(img_io, mimetype='image/png')

    except Exception as e:
        print(f"error in color_point processing image: {e}")
        return "image process failed", 500
    
if __name__ == '__main__':
    import json
    app.run(host='0.0.0.0', port=5000)
