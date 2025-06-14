import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:http/http.dart' as http;
import 'package:flutter/services.dart'; // for vibration
import 'dart:convert';

void main() => runApp(MyApp());

class MyApp extends StatefulWidget {
  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  late stt.SpeechToText _speech;
  bool _isListening = false;
  String _text = "음성 입력을 시작하세요";

  final String baseUrl = 'https://thankful-smashing-raven.ngrok-free.app';

  @override
  void initState() {
    super.initState();
    _speech = stt.SpeechToText();
  }

  void _startListening() async {
    if (!_isListening) {
      bool available = await _speech.initialize();
      if (available) {
        setState(() => _isListening = true);

        // 진동: 약하게 100ms
        HapticFeedback.lightImpact();

        _speech.listen(
          onResult: (result) {
            setState(() => _text = result.recognizedWords);
          },
          listenMode: stt.ListenMode.dictation,
        );
      }
    }
  }

  void _stopListeningAndSendText() async {
    if (_isListening) {
      setState(() => _isListening = false);
      await _speech.stop();

      try {
        var uri = Uri.parse('$baseUrl/text-trigger');
        var response = await http.post(
          uri,
          headers: {"Content-Type": "application/json"},
          body: jsonEncode({"text": _text}),
        );

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('텍스트 전송 완료: ${response.statusCode}')),
        );
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('텍스트 전송 실패')),
        );
      }
    }
  }

  void _sendEmotionTrigger() async {
    try {
      var uri = Uri.parse('$baseUrl/emotion-trigger');
      var response = await http.post(uri);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('감정 트리거 전송 완료: ${response.statusCode}')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('감정 트리거 전송 실패')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: Text('STT 제어')),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(_text, style: TextStyle(fontSize: 20)),
                SizedBox(height: 40),
                ElevatedButton.icon(
                  icon: Icon(Icons.mic),
                  label: Text(_isListening ? '듣는 중...' : '음성 입력 시작'),
                  onPressed: _startListening,
                ),
                SizedBox(height: 10),
                ElevatedButton.icon(
                  icon: Icon(Icons.send),
                  label: Text('텍스트 트리거 전송'),
                  onPressed: _stopListeningAndSendText,
                ),
                SizedBox(height: 10),
                ElevatedButton.icon(
                  icon: Icon(Icons.face),
                  label: Text('감정 트리거 전송'),
                  onPressed: _sendEmotionTrigger,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
