# 🎨 ColorMyModel - Advanced Model Painting Guide App

A sophisticated application designed to assist model painters in identifying and segmenting regions for painting, with advanced color code detection.

## ✨ Features

- **Intelligent Region Segmentation**: Automatically identifies and segments different areas of your model
- **Color Code Detection**: Advanced OCR for detecting various color codes (H, XF, TS, X series)
- **Multi-language Support**: Handles Japanese, Chinese, and English text
- **Interactive UI**: User-friendly interface for selecting and managing paint regions
- **Real-time Processing**: Fast and efficient image processing
- **High Accuracy**: Enhanced preprocessing for better OCR results

## 💻 Technology Stack

### Frontend
- **Framework**: Flutter (iOS/Android/Web support)
- **UI Components**: Material Design
- **State Management**: Provider/Riverpod
- **Image Handling**: Image Picker, File Selector

### Backend
- **Server**: Flask RESTful API
- **Image Processing**:
  - OpenCV (Advanced edge detection and segmentation)
  - NumPy (Numerical operations)
  - Pillow (Image manipulation)
- **OCR Engine**:
  - EasyOCR (Multi-language support)
  - Enhanced preprocessing pipeline
- **Machine Learning**:
  - scikit-learn (K-means clustering)
  - Custom color generation algorithms

### Development Tools
- **Version Control**: Git
- **Documentation**: Markdown
- **Code Quality**: Flutter Lints
- **Testing**: Flutter Test

## 🚀 Getting Started

1. **Prerequisites**:
   - Flutter SDK
   - Python 3.8+
   - Required Python packages: `opencv-python`, `numpy`, `easyocr`, `flask`, `pillow`

2. **Installation**:
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/ColorMyModel.git

   # Install Flutter dependencies
   flutter pub get

   # Install Python dependencies
   pip install -r requirements.txt
   ```

3. **Running the App**:
   ```bash
   # Start the Flask backend
   python main.py

   # Run the Flutter app
   flutter run
   ```

## 📝 Usage

1. Launch the app and select an image of your model
2. Choose the processing mode:
   - Region segmentation
   - Color code detection
   - Combined analysis
3. View the results and interact with the segmented regions
4. Export or save your results

## 🛠 Advanced Features

- **Enhanced Preprocessing**: Multiple preprocessing stages for optimal results
- **Smart Color Generation**: Visually distinct colors for better region identification
- **Error Handling**: Robust error detection and recovery
- **Performance Optimization**: Efficient processing for various image sizes

## 📋 Project Status

Current development focus:
- Improving OCR accuracy for complex color codes
- Enhancing region segmentation for intricate models
- Optimizing performance for large images
- Adding more color mapping options

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
