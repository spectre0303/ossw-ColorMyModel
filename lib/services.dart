import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'config.dart';

class NetworkService {
  static const Duration timeoutDuration = Duration(seconds: 30);
  static const int maxRetries = 3;
  static const Duration retryDelay = Duration(seconds: 1);

  static Future<T> handleResponse<T>(Future<http.Response> Function() request) async {
    int attempts = 0;
    while (attempts < maxRetries) {
      try {
        final response = await request().timeout(timeoutDuration);
        
        if (response.statusCode == 200) {
          return json.decode(response.body) as T;
        } else if (response.statusCode >= 500) {
          // Server errors might be temporary, so we'll retry
          attempts++;
          if (attempts < maxRetries) {
            await Future.delayed(retryDelay * attempts);
            continue;
          }
        }
        throw HttpException('${response.statusCode}: ${response.body}');
      } on TimeoutException {
        attempts++;
        if (attempts < maxRetries) {
          await Future.delayed(retryDelay * attempts);
          continue;
        }
        throw TimeoutException('Request timed out after $attempts attempts');
      } on SocketException catch (e) {
        attempts++;
        if (attempts < maxRetries) {
          await Future.delayed(retryDelay * attempts);
          continue;
        }
        throw Exception('Network error after $attempts attempts: $e');
      } catch (e) {
        throw Exception('Error: $e');
      }
    }
    throw Exception('Failed after $maxRetries attempts');
  }

  static Future<Map<String, dynamic>> uploadImage(String path, Uint8List imageBytes, String mode) async {
    final request = http.MultipartRequest('POST', Uri.parse(Config.uploadEndpoint))
      ..files.add(
        http.MultipartFile.fromBytes('file', imageBytes, filename: path),
      )
      ..fields['mode'] = mode;

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);
    
    return handleResponse<Map<String, dynamic>>(() => Future.value(response));
  }

  static Future<Uint8List> colorPoint(Uint8List imageBytes, double x, double y, String color) async {
    final request = http.MultipartRequest('POST', Uri.parse(Config.colorPointEndpoint))
      ..fields['data'] = jsonEncode({'x': x, 'y': y, 'color': color})
      ..files.add(
        http.MultipartFile.fromBytes('image', imageBytes, filename: 'image.png'),
      );

    final streamedResponse = await request.send();
    return streamedResponse.stream.toBytes();
  }
}

class UIHelper {
  static void showErrorDialog(BuildContext context, String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Error'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('OK'),
          ),
        ],
      ),
    );
  }

  static Future<void> showLoadingDialog(BuildContext context) async {
    return showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => Center(
        child: Container(
          padding: EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircularProgressIndicator(),
              SizedBox(height: 16),
              Text('Processing...'),
            ],
          ),
        ),
      ),
    );
  }
}
