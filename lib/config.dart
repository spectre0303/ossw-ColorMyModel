class Config {
  static const bool isDevelopment = true;

  // Server URLs
  static const String devServerUrl = 'http://localhost:5000';
  static const String prodServerUrl = 'http://192.168.219.101:5000';

  // Get the appropriate server URL based on environment
  static String get serverUrl => isDevelopment ? devServerUrl : prodServerUrl;

  // API endpoints
  static String get uploadEndpoint => '$serverUrl/upload';
  static String get colorPointEndpoint => '$serverUrl/color_point';
  static String get ocrEndpoint => '$serverUrl/ocr';
}
