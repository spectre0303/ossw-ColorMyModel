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

        print("이미지 2개 전송 준비 완료")
        return jsonify({
            'grayscale': grayscale_b64,
            'inverted': inverted_b64
        })

    except Exception as e:
        print(f"error in processing image: {e}")
        return "image process failed", 500

from PIL import ImageDraw, ImageShow  # ImageDraw도 import 필요


@app.route('/ocr', methods=['POST'])
def ocr_image():
    file = request.files.get('image')
    if not file:
        return "Bad Request: Image file required", 400

    client_ip = request.remote_addr
    count = click_counts.get(client_ip, 0) + 1
    click_counts[client_ip] = count

    try:
        img = Image.open(file.stream).convert("RGB")
        img_np = np.array(img)
        print(f"[OCR 요청] 클라이언트 IP: {client_ip}, 이미지 shape: {img_np.shape}")

        codes, texts = run_ocr_on_image(img_np)

        print(f"클라이언트 {client_ip}의 현재 클릭 횟수: {count}")
        print(f"인식된 코드들: {codes}")
        print(f"인식된 텍스트들: {texts}")

        return jsonify({
            'codes': codes,
            'texts': texts
        })

    except Exception as e:
        print(f"error in OCR processing image: {e}")
        return "image process failed", 500

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
