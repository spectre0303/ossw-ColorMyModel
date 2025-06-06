import 'dart:convert';
// File 클래스 사용
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart'; // ESC 키 이벤트용
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
// ZIP 파일 처리

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ColorMyModel',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.redAccent),
      ),
      home: const MyHomePage(title: 'ColorMyModel'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});
  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final Map<String, String> modeMap = {
    '1': '1. 숫자 + 표',
    '2': '2. 타미야 도료 (XF-??) 기준',
    '3': '3. 군제 (현 미스터하비 도료) 기준',
    '4': '4. 색상 단어',
  };

  String? selectedMode;

  Future<void> _pickImage(BuildContext context) async {
    final ImagePicker picker = ImagePicker();
    final XFile? image = await picker.pickImage(source: ImageSource.gallery);

    if (image == null) return;

    if (selectedMode == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("모드를 선택해주세요.")),
      );
      return;
    }

    try {
      final bytes = await image.readAsBytes();
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('http://192.168.219.101:5000/upload'),
      );

      request.files.add(
        http.MultipartFile.fromBytes('image', bytes, filename: image.name),
      );

      request.fields['mode'] = selectedMode!;

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
        title: Text(widget.title),
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
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
              DropdownButtonFormField<String>(
                decoration: const InputDecoration(
                  labelText: "Select a Mode",
                  border: OutlineInputBorder(),
                ),
                value: selectedMode,
                items: modeMap.entries
                    .map((entry) => DropdownMenuItem(
                          value: entry.key,
                          child: Text(entry.value),
                        ))
                    .toList(),
                onChanged: (val) => setState(() => selectedMode = val),
              ),
              const SizedBox(height: 30),
              FloatingActionButton.extended(
                onPressed: () => _pickImage(context),
                icon: const Icon(Icons.photo_album),
                label: const Text("Upload your blueprint!"),
              ),
              const SizedBox(height: 20),
              ElevatedButton.icon(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const HelpPage()),
                  );
                },
                icon: const Icon(Icons.help_outline),
                label: const Text("Help me!"),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
class HelpPage extends StatelessWidget {
  const HelpPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Help & Guide")),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // 이미지
              Image.asset('assets/example.jpg'),

              const SizedBox(height: 20),

              // 텍스트 박스 (위쪽)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  border: Border.all(color: Colors.redAccent),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Text(
                   '앱이나 복사기를 통해 도면을 선명하게 스캔한 이미지를 올리길 권장합니다. 사진을 직접 찍어 올릴시, 구겨지거나 접힌 곳이 최대한 없도록 평평하게 한 이후 그림자 진곳 없이 촬영하기를 권장합니다. 도면의 그림 자체에 입체감을 위한 명암이 존재할 시 결과에 영향을 줄 수 있습니다. (이를 준수하지 않은 업로드 파일에 대한 결과는 책임지지 않습니다. 위는 예시 이미지입니다.)',
                  style: TextStyle(fontSize: 16),
                ),
              ),

              const SizedBox(height: 20),

              // 텍스트 박스 (아래쪽)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  border: Border.all(color: Colors.blueAccent),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Text(
                  '우리는 색상 표기의 4가지의 형식만 제공하고 있습니니다,\n 1. 숫자 + 표 \n 2. 타미야 도료(XF-??) 기준\n 3. 군제(현 미스터하비 도료) 기준\n 4. 색상 단어',
                  style: TextStyle(fontSize: 16),
                ),
              ),
            ],
          ),
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
  final GlobalKey imageKey = GlobalKey();

  final List<String> colors = [
    'RED', 'GREEN', 'BLUE', 'YELLOW', 'ORANGE', 'PURPLE', 'PINK', 'BLACK', 'WHITE'
  ];

  final TextEditingController searchController = TextEditingController();
  List<String> filteredColors = [];
  bool showSearchResults = false;

  @override
  void initState() {
    super.initState();
    currentImageBytes = Uint8List.fromList(widget.imageBytes);
    filteredColors = List.from(colors);
  }

  void updateSearch(String query) {
    final q = query.trim().toUpperCase();
    if (q.isEmpty) {
      filteredColors = List.from(colors);
      showSearchResults = false;
    } else {
      filteredColors = colors.where((c) => c.contains(q)).toList();
      showSearchResults = true;
    }
    setState(() {});
  }

  void selectColor(String color) {
    selectedColor = color;
    searchController.clear();
    showSearchResults = false;
    setState(() {});
  }

  @override
  void dispose() {
    searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Shortcuts(
      shortcuts: {
        LogicalKeySet(LogicalKeyboardKey.escape): const ActivateIntent(),
      },
      child: Actions(
        actions: {
          ActivateIntent: CallbackAction<Intent>(
            onInvoke: (_) {
              setState(() {
                isSelecting = false;
                selectedColor = null;
              });
              return null;
            },
          ),
        },
        child: Scaffold(
          appBar: AppBar(title: const Text("Image Preview")),
          body: Center(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  flex: 4,
                  child: GestureDetector(
                    onTapDown: (TapDownDetails details) async {
                      if (selectedColor != null && isSelecting) {
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
                        key: imageKey,
                      ),
                    ),
                  ),
                ),

                // 우측 사이드 바
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

                    // 검색창
                    SizedBox(
                      width: 150,
                      child: TextField(
                        controller: searchController,
                        decoration: const InputDecoration(
                          prefixIcon: Icon(Icons.search),
                          hintText: 'Search color',
                          border: OutlineInputBorder(),
                          isDense: true,
                        ),
                        onChanged: updateSearch,
                      ),
                    ),

                    // 검색 결과
                    if (showSearchResults)
                      Container(
                        width: 150,
                        height: 100,
                        margin: const EdgeInsets.only(top: 8),
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.grey),
                          color: Colors.white,
                        ),
                        child: ListView.builder(
                          itemCount: filteredColors.length,
                          itemBuilder: (context, index) {
                            final color = filteredColors[index];
                            return ListTile(
                              title: Text(color),
                              onTap: () => selectColor(color),
                              dense: true,
                            );
                          },
                        ),
                      )
                    else
                      const SizedBox(height: 8),

                    // 드롭다운
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
                      ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
