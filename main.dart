import 'dart:typed_data';
import 'dart:convert';
import 'dart:io'; // File 클래스 사용
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart'; // ESC 키 이벤트용
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:archive/archive.dart'; // ZIP 파일 처리

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ColorMyModel',
      theme: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: Colors.redAccent)),
      home: const MyHomePage(title: 'ColorMyModel')
    );
  }
}


class MyHomePage extends StatelessWidget {
  const MyHomePage({super.key, required this.title});
  final String title;

  Future<void> _pickImage(BuildContext context) async {
    final ImagePicker picker = ImagePicker();
    final XFile? image = await picker.pickImage(source: ImageSource.gallery);

    if (image == null) return;

    try {
      final bytes = await image.readAsBytes();
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('http://192.168.219.101:5000/upload'),
      );
      request.files.add(
        http.MultipartFile.fromBytes('image', bytes, filename: image.name),
      );

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final jsonData = jsonDecode(response.body);

        final grayscaleBytes = base64Decode(jsonData['grayscale']);
        final invertedBytes = base64Decode(jsonData['inverted']);

        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => DualImagePreviewScreen(
              grayscale: grayscaleBytes,
              inverted: invertedBytes,
            ),
          ),
        );
      } else {
        debugPrint('서버 오류: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint("전송 오류: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Padding(
              padding: EdgeInsets.only(bottom: 24.0),
              child: Text(
                "This application can color your ship plamodel's blueprint for painting!",
                textAlign: TextAlign.center,
              ),
            ),
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                FloatingActionButton(
                  onPressed: () {
                    _pickImage(context);
                  },
                  tooltip: "Upload your blueprint!",
                  child: const Icon(Icons.photo_album),
                ),
                const SizedBox(width: 20),
                FloatingActionButton(
                  onPressed: () {
                    // Help 버튼 기능 필요 시 추가
                  },
                  tooltip: "Help Me!",
                  child: const Icon(Icons.help),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class DualImagePreviewScreen extends StatelessWidget {
  final Uint8List grayscale;
  final Uint8List inverted;

  const DualImagePreviewScreen({
    super.key,
    required this.grayscale,
    required this.inverted,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Processed Images")),
      body: SingleChildScrollView(
        child: Center(
          child: Column(
            children: [
              const SizedBox(height: 16),

              // Grayscale 이미지 + 버튼
              Column(
                children: [
                  const Text(
                    "option 01",
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: Image.memory(
                      grayscale,
                      fit: BoxFit.contain,
                      height: MediaQuery.of(context).size.height * 0.4,
                    ),
                  ),
                  ElevatedButton(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => ImagePreviewScreen(imageBytes: grayscale),
                        ),
                      );
                    },
                    child: const Text("Select This!"),
                  ),
                ],
              ),

              const SizedBox(height: 32),

              // Inverted 이미지 + 버튼
              Column(
                children: [
                  const Text(
                    "option 02",
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: Image.memory(
                      inverted,
                      fit: BoxFit.contain,
                      height: MediaQuery.of(context).size.height * 0.4,
                    ),
                  ),
                  ElevatedButton(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => ImagePreviewScreen(imageBytes: inverted),
                        ),
                      );
                    },
                    child: const Text("Select This!"),
                  ),
                ],
              ),

              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }
}


class ImagePreviewScreen extends StatefulWidget {
  final Uint8List imageBytes;

  const ImagePreviewScreen({super.key, required this.imageBytes});

  @override
  State<ImagePreviewScreen> createState() => _ImagePreviewScreenState();
}

class _ImagePreviewScreenState extends State<ImagePreviewScreen> {
  late Uint8List currentImageBytes;
  String? selectedColor;
  bool isSelecting = true;
  final GlobalKey imageKey = GlobalKey(); // 🔑 이미지 위젯 추적용 키

  final List<String> colors = ['RED', 'GREEN', 'BLUE'];

  @override
  void initState() {
    super.initState();
    currentImageBytes = Uint8List.fromList(widget.imageBytes);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Image Preview")),
      body: RawKeyboardListener(
        focusNode: FocusNode()..requestFocus(),
        onKey: (event) {
          if (event.logicalKey == LogicalKeyboardKey.escape) {
            setState(() {
              isSelecting = false;
              selectedColor = null;
            });
          }
        },
        child: Center(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                flex: 4,
                child: GestureDetector(
                  onTapDown: (TapDownDetails details) async {
                    if (selectedColor != null && isSelecting) {
                      // 🔍 정확한 이미지 위치 기준 계산
                      final RenderBox box = imageKey.currentContext!.findRenderObject() as RenderBox;
                      final Offset widgetPosition = box.localToGlobal(Offset.zero);
                      final Size widgetSize = box.size;

                      final ui.Image decodedImage = await decodeImageFromList(currentImageBytes);
                      final int imageWidth = decodedImage.width;
                      final int imageHeight = decodedImage.height;

                      final double widgetWidth = widgetSize.width;
                      final double widgetHeight = widgetSize.height;

                      final double imgAspect = imageWidth / imageHeight;
                      final double widgetAspect = widgetWidth / widgetHeight;

                      double scale, offsetX = 0, offsetY = 0;

                      if (imgAspect > widgetAspect) {
                        scale = widgetWidth / imageWidth;
                        offsetY = (widgetHeight - imageHeight * scale) / 2;
                      } else {
                        scale = widgetHeight / imageHeight;
                        offsetX = (widgetWidth - imageWidth * scale) / 2;
                      }

                      final Offset tapGlobalPos = details.globalPosition;
                      final Offset localPos = tapGlobalPos - widgetPosition;

                      final double imageX = ((localPos.dx - offsetX) / scale).clamp(0, imageWidth - 1);
                      final double imageY = ((localPos.dy - offsetY) / scale).clamp(0, imageHeight - 1);

                      debugPrint('✅ 보정된 클릭 좌표: ($imageX, $imageY)');

                      final uri = Uri.parse('http://192.168.219.101:5000/color_point');
                      final request = http.MultipartRequest('POST', uri);
                      request.fields['data'] = jsonEncode({'x': imageX, 'y': imageY, 'color': selectedColor});
                      request.files.add(http.MultipartFile.fromBytes('image', currentImageBytes, filename: 'image.png'));

                      try {
                        final response = await request.send();
                        if (response.statusCode == 200) {
                          final bytes = await response.stream.toBytes();
                          setState(() {
                            currentImageBytes = bytes;
                            selectedColor = null;
                          });
                        } else {
                          debugPrint('서버 오류: ${response.statusCode}');
                        }
                      } catch (e) {
                        debugPrint('요청 실패: $e');
                      }
                    }
                  },
                  child: Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: Image.memory(
                      currentImageBytes,
                      fit: BoxFit.contain,
                      key: imageKey, // ✅ 여기에 키 설정
                    ),
                  ),
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  const RotatedBox(
                    quarterTurns: 3,
                    child: Text(
                      "output retouch phase",
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                  ),
                  const SizedBox(height: 20),
                  DropdownButton<String>(
                    hint: const Text("color"),
                    value: selectedColor,
                    items: colors
                        .map((color) => DropdownMenuItem(value: color, child: Text(color)))
                        .toList(),
                    onChanged: (value) {
                      setState(() {
                        selectedColor = value;
                      });
                    },
                  ),
                  if (!isSelecting)
                    const Padding(
                      padding: EdgeInsets.only(top: 16),
                      child: Text("선택 종료됨 (ESC)"),
                    )
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
