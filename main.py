from flask import Flask, request, send_file
import io
from PIL import Image
from flask_cors import CORS
from PIL import ImageDraw, ImageShow  # ImageDraw도 import 필요
from flask import Flask, request, send_file
import io
from PIL import Image, ImageDraw
import json


app = Flask(__name__)
CORS(app)

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
        print(f"{client_ip}의 현재 클릭 횟수: {count}")

        img = Image.open(file.stream)

        # 홀수번째엔 흑백, 짝수번째엔 컬러 유지 (기존 규칙 유지)
        if count % 2 == 1:
            processed = img.convert("L")
            print("처리: 흑백 변환")
        else:
            processed = img.convert("RGB")
            print("처리: 컬러 유지")

        img_io = io.BytesIO()
        processed.save(img_io, 'PNG')
        img_io.seek(0)

        print("이미지 돌려드림")
        return send_file(img_io, mimetype='image/png')

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

    print(f"[좌표 클릭] 클라이언트 IP: {client_ip}, x={x}, y={y}, color={color}")
    print(f"{client_ip}의 현재 클릭 횟수: {count}")

    file = request.files.get('image')
    if not file:
        return "Bad Request: Image file required", 400

    try:
        img = Image.open(file.stream)

        if count % 2 == 1:
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
        else:
            processed = img.convert("L")
            print("color_point 처리: 흑백 변환")

        # 디버깅용: 점 찍은 이미지를 따로 복사해서 만들기
        debug_img = processed.copy()
        draw = ImageDraw.Draw(debug_img)
        radius = 5
        left_up = (x - radius, y - radius)
        right_down = (x + radius, y + radius)
        draw.ellipse([left_up, right_down], fill=(255, 255, 255))  # 하얀색 점으로 변경

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
