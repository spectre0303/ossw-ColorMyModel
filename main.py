from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image, ImageOps
import io
import base64
import zipfile
import os

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
        grayscale = img.convert("L")
        inverted = ImageOps.invert(img.convert("RGB"))

        # 각각을 Base64로 인코딩
        def image_to_base64(image_obj):
            img_io = io.BytesIO()
            image_obj.save(img_io, format='PNG')
            img_io.seek(0)
            return base64.b64encode(img_io.read()).decode('utf-8')

        grayscale_b64 = image_to_base64(grayscale)
        inverted_b64 = image_to_base64(inverted)

        print("이미지 2개 전송 준비 완료")
        return jsonify({
            'grayscale': grayscale_b64,
            'inverted': inverted_b64
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
        img = Image.open(file.stream).convert("RGB")  # 항상 RGB로 변환하여 안정성 확보


        # 선택 색상 기반 변환
        gray = img.convert("L")
        color_map = {
            'RED': (255, 0, 0),
            'GREEN': (0, 255, 0),
            'BLUE': (0, 0, 255),
            'PURPLE': (128, 0, 128),
        }
        base_color = color_map.get(color.upper(), (255, 255, 255))

        r = gray.point(lambda p: p * base_color[0] / 255)
        g = gray.point(lambda p: p * base_color[1] / 255)
        b = gray.point(lambda p: p * base_color[2] / 255)
        processed = Image.merge("RGB", (r, g, b))

        print("color_point 처리: 선택 색상톤으로 컬러 변환")


        # 디버깅용 점 추가
        debug_img = processed.copy()
        draw = ImageDraw.Draw(debug_img)
        radius = 5
        left_up = (x - radius, y - radius)
        right_down = (x + radius, y + radius)
        draw.ellipse([left_up, right_down], fill=(255, 255, 255))  # 하얀 점

        # 디버깅 확인용: 디스플레이
        ImageShow.show(debug_img)

        img_io = io.BytesIO()
        processed.save(img_io, 'PNG')
        img_io.seek(0)

        print("color_point 이미지(점 없이) 돌려드림")
        return send_file(img_io, mimetype='image/png')

    except Exception as e:
        print(f"error in color_point processing image: {e}")
        return "image process failed", 500

if __name__ == '__main__':
    import json
    app.run(host='0.0.0.0', port=5000)
