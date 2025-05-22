# server.py
from flask import Flask, request, send_file
import io
from PIL import Image
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['POST'])
def upload_image():
    file = request.files['image']

    # 로그 출력: 요청자 IP, 파일명 등
    print(f"요청 받음 - 클라이언트 IP: {request.remote_addr}")
    print(f"업로드된 파일 이름: {file.filename}")

    try:
        img = Image.open(file.stream)

        # 예시 처리: 이미지를 흑백으로 변환
        processed = img.convert("L")

        # 이미지 메모리에 저장
        img_io = io.BytesIO()
        processed.save(img_io, 'PNG')
        processed.show()
        img_io.seek(0)

        print("이미지 돌려드림")
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        print(f"error in processing image: {e}")
        return "image process failed", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)