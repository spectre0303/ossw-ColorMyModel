from flask import Flask, request, jsonify, send_file
from region_segment_ver1 import segment_and_colorize_ver1
from region_segment_ver2 import segment_and_colorize_ver2
from flask_cors import CORS
from PIL import Image, ImageOps
import io
import base64
import numpy as np
import cv2
import time
import psutil
from PreprocessAndOCR import run_ocr_on_image
import logging
import traceback
import sys
from logging.handlers import RotatingFileHandler
from typing import Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add file handler with rotation
handler = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=3)
handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))
logger.addHandler(handler)

# Global state
click_counts: Dict[str, int] = {}
processing_stats: Dict[str, Any] = {
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'last_error': None,
    'last_error_time': None
}

app = Flask(__name__)

# Configure CORS with specific options
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:*",
            "http://127.0.0.1:*",
            "http://192.168.*.*:*"  # Allow local network access
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

def update_error_stats(error: Exception) -> None:
    processing_stats['failed_requests'] += 1
    processing_stats['last_error'] = str(error)
    processing_stats['last_error_time'] = datetime.now().isoformat()

@app.after_request
def add_security_headers(response):
    response.headers.update({
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'",
    })
    return response

def handle_error_with_logging(error):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    logger.error(f"Exception type: {exc_type.__name__}")
    logger.error(f"Exception message: {str(exc_value)}")
    logger.error("Traceback:")
    for line in traceback.extract_tb(exc_traceback).format():
        logger.error(line)
    
    update_error_stats(error)
    
    error_msg = str(error)
    if app.debug:
        error_msg = f"{str(error)}\n{''.join(traceback.format_tb(exc_traceback))}"
    
    return jsonify({
        "status": "error",
        "message": error_msg,
        "error_type": exc_type.__name__
    }), 500

@app.errorhandler(Exception)
def handle_error(error):
    return handle_error_with_logging(error)

@app.before_request
def log_request_info():
    processing_stats['total_requests'] += 1
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    if request.form:
        logger.info(f"Form data: {dict(request.form)}")

@app.after_request
def log_response_info(response):
    if response.status_code == 200:
        processing_stats['successful_requests'] += 1
    logger.info(f"Response Status: {response.status}")
    return response

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        # Validate request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Validate image file
        from validators import validate_image_file
        validate_image_file(file)
        
        # Read and process image
        image_bytes = file.read()
        img = Image.open(io.BytesIO(image_bytes))
        img = ImageOps.exif_transpose(img)  # Handle EXIF orientation
        
        # Process image based on version
        version = request.form.get('version', '1')
        if version == '2':
            result_image = segment_and_colorize_ver2(img)
        else:
            result_image = segment_and_colorize_ver1(img)
            
        # Convert result to base64
        buffered = io.BytesIO()
        result_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            "status": "success",
            "image": img_str
        })
        
    except Exception as e:
        logger.error(f"Error processing image upload: {str(e)}")
        return handle_error_with_logging(e)

@app.route('/ocr', methods=['POST'])
def ocr_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400
            
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        # Convert to numpy array for OCR
        img_bytes = file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Failed to decode image")
            
        # Run OCR with enhanced preprocessing
        codes, texts = run_ocr_on_image(img)
        
        return jsonify({
            "status": "success",
            "codes": codes,
            "texts": texts
        })
        
    except Exception as e:
        logger.error(f"Error processing OCR request: {str(e)}")
        return handle_error_with_logging(e)

@app.route('/color_point', methods=['POST'])
def color_point():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
            
        data = request.json
        if not data or 'x' not in data or 'y' not in data:
            return jsonify({"error": "Invalid coordinates"}), 400
            
        x, y = float(data['x']), float(data['y'])
        point_id = f"{x},{y}"
        
        click_counts[point_id] = click_counts.get(point_id, 0) + 1
        
        return jsonify({
            "status": "success",
            "point": point_id,
            "clicks": click_counts[point_id]
        })
        
    except Exception as e:
        logger.error(f"Error processing color point request: {str(e)}")
        return handle_error_with_logging(e)

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get server statistics and health information."""
    return jsonify({
        "status": "success",
        "stats": processing_stats
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify server status and dependencies."""
    try:
        # Check if we can create a small test image
        test_img = Image.new('RGB', (1, 1))
        
        # Check if OpenCV is working
        test_arr = np.zeros((1, 1, 3), dtype=np.uint8)
        cv2.resize(test_arr, (2, 2))
        
        # Memory usage stats
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return jsonify({
            "status": "healthy",
            "uptime": time.time() - process.create_time(),
            "memory_usage": {
                "rss": memory_info.rss / 1024 / 1024,  # MB
                "vms": memory_info.vms / 1024 / 1024   # MB
            },
            "processing_stats": processing_stats,
            "dependencies": {
                "PIL": True,
                "OpenCV": True,
                "NumPy": True
            }
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    logger.info("Starting server on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
