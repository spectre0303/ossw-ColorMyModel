import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io'; // File 클래스를 사용하기 위해 임포트

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

class MyHomePage extends StatelessWidget {
  const MyHomePage({super.key, required this.title});
  final String title;

  Future<void> _pickImage(BuildContext context) async {
  final ImagePicker picker = ImagePicker();

  if (kIsWeb) {
      // 웹은 갤러리만 지원
      final XFile? image = await picker.pickImage(source: ImageSource.gallery);
      if (image != null) {
        print("웹에서 선택한 사진 경로: ${image.path}");
      }

      if (image != null) {
      // 이미지 선택 후, 새로운 화면으로 넘어가기
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => ImagePreviewScreen(imagePath: image.path),
        ),
      );
    }
      return;
    }

    

  showModalBottomSheet(
    context: context,
    builder: (BuildContext ctx) {
      return SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.camera_alt),
              title: const Text("카메라로 촬영"),
              onTap: () async {
                final XFile? photo = await picker.pickImage(source: ImageSource.camera);
                Navigator.pop(ctx);
                if (photo != null) {
                  // 사진 사용 처리
                  print("촬영한 사진 경로: ${photo.path}");
                }
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library),
              title: const Text("갤러리에서 선택"),
              onTap: () async {
                final XFile? image = await picker.pickImage(source: ImageSource.gallery);
                Navigator.pop(ctx);
                if (image != null) {
                  // 사진 사용 처리
                  print("선택한 사진 경로: ${image.path}");
                }
              },
            ),
          ],
        ),
      );
    },
  );
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
                    print("Button 1 pressed");
                    _pickImage(context);
                  },
                  tooltip: "Upload your blueprint!",
                  child: const Icon(Icons.photo_album),
                ),
                const SizedBox(width: 20),
                FloatingActionButton(
                  onPressed: () {
                    print("Button 2 pressed");
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


class ImagePreviewScreen extends StatelessWidget {
  final String imagePath;
  const ImagePreviewScreen({super.key, required this.imagePath});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Image Preview")),
      body: Center(
        child: kIsWeb
          ?Image.network(imagePath) // 웹에서 선택한 이미지를 화면에 표시
          :Image.file(File(imagePath))// 선택한 이미지를 화면에 표시
      ),
    );
  }
}