import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
//import 'dart:io' show Platform;
import 'package:flutter/foundation.dart';
import 'dart:io'; // File 클래스를 사용하기 위해 임포트
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart'; // For ESC
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:ui' as ui;

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

    if (kIsWeb) {
      // 웹은 갤러리만 지원
      final XFile? image = await picker.pickImage(source: ImageSource.gallery);
      if (image != null) {
        if (kDebugMode) debugPrint("웹에서 선택한 사진 경로: ${image.path}");
        Uint8List responseBytes = Uint8List(0);
        try {
          final bytes = await image.readAsBytes();
          final request = http.MultipartRequest('POST', Uri.parse('http://192.168.219.101:5000/upload'));
          request.files.add(http.MultipartFile.fromBytes('image', bytes, filename: image.name));

          final response = await request.send();
          if (response.statusCode == 200) {
            responseBytes = await response.stream.toBytes();
            Navigator.pushReplacement(context, MaterialPageRoute(builder: (context) => ImagePreviewScreen(imageBytes: responseBytes)));
          } 
          else {
            if (kDebugMode) debugPrint("서버 오류: ${response.statusCode}");
          }
        }
        catch (e) {
          if (kDebugMode) debugPrint("에러 발생: $e");
          Navigator.pushAndRemoveUntil(context, MaterialPageRoute(builder: (context) => const MyHomePage(title: 'ColorMyModel')), (Route<dynamic> route) => false);
        }
        finally {
          if (kDebugMode) debugPrint("서버 통신 완료");
        }

        return;
      }

      showModalBottomSheet(
        context: context,
        builder: (BuildContext ctx) {
          ListTile l1 = ListTile(
            leading: const Icon(Icons.camera_alt),
            title: const Text("카메라로 촬영"),
            onTap: () async {
              final XFile? photo = await picker.pickImage(source: ImageSource.camera);
              Navigator.pop(ctx);
              if (photo != null) {
                // 사진 사용 처리
                if (kDebugMode) debugPrint("촬영한 사진 경로: ${photo.path}");
              }
            }
          );
          ListTile l2 = ListTile(
            leading: const Icon(Icons.photo_library),
            title: const Text("갤러리에서 선택"),
            onTap: () async {
              final XFile? image = await picker.pickImage(source: ImageSource.gallery);
              Navigator.pop(ctx);
              if (image != null) {
                // 사진 사용 처리
                if (kDebugMode) debugPrint("선택한 사진 경로: ${image.path}");
              }
            }
          );
          return SafeArea(child: Column(mainAxisSize: MainAxisSize.min, children: [l1, l2]));
        }
      );
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(backgroundColor: Theme.of(context).colorScheme.inversePrimary, title: Text(title)),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Padding(
              padding: EdgeInsets.only(bottom: 24.0),
              child: Text(
                "This application can color your ship plamodel's blueprint for painting!",
                textAlign: TextAlign.center,
              )
            ),
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                FloatingActionButton(
                  onPressed: () {
                    if (kDebugMode) debugPrint("Button 1 pressed");
                    _pickImage(context);
                  },
                  tooltip: "Upload your blueprint!",
                  child: const Icon(Icons.photo_album),
                ),
                const SizedBox(width: 20),
                FloatingActionButton(
                  onPressed: () {
                    if (kDebugMode) debugPrint("Button 2 pressed");
                  },
                  tooltip: "Help Me!",
                  child: const Icon(Icons.help),
                )
              ]
            )
          ]
        )
      )
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

