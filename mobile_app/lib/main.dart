import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:http/http.dart' as http;
import 'package:flutter/services.dart';
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
  TextEditingController _urlController = TextEditingController();
  String _baseUrl = '';

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

  void _stopListeningAndSendText(BuildContext context) async {
    if (_isListening) {
      setState(() => _isListening = false);
      await _speech.stop();

      if (_baseUrl.isEmpty) {
        _showError(context, '서버 주소를 먼저 입력해주세요.');
        return;
      }

      try {
        var uri = Uri.parse('$_baseUrl/text-trigger');
        var response = await http.post(
          uri,
          headers: {"Content-Type": "application/json"},
          body: jsonEncode({"text": _text}),
        );
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('텍스트 전송 완료: ${response.statusCode}')),
        );
      } catch (e) {
        _showError(context, '텍스트 전송 실패');
      }
    }
  }

  void _sendEmotionTrigger(BuildContext context) async {
    if (_baseUrl.isEmpty) {
      _showError(context, '서버 주소를 먼저 입력해주세요.');
      return;
    }

    try {
      var uri = Uri.parse('$_baseUrl/emotion-trigger');
      var response = await http.post(uri);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('감정 트리거 전송 완료: ${response.statusCode}')),
      );
    } catch (e) {
      _showError(context, '감정 트리거 전송 실패');
    }
  }

  void _sendResetTrigger(BuildContext context) async {
    if (_baseUrl.isEmpty) {
      _showError(context, '서버 주소를 먼저 입력해주세요.');
      return;
    }

    try {
      var uri = Uri.parse('$_baseUrl/reset');
      var response = await http.post(uri);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('리셋 완료: ${response.statusCode}')),
      );
    } catch (e) {
      _showError(context, '리셋 실패');
    }
  }

  void _fetchServerStatus(BuildContext context) async {
    if (_baseUrl.isEmpty) {
      _showError(context, '서버 주소를 먼저 입력해주세요.');
      return;
    }

    try {
      var uri = Uri.parse('$_baseUrl/status');
      var response = await http.get(uri);

      if (response.statusCode == 200) {
        var data = jsonDecode(response.body);
        showDialog(
          context: context,
          builder: (_) => AlertDialog(
            title: Text("서버 상태"),
            content: Text('''
감정 트리거: ${data['emotion_triggered']}
텍스트 트리거: ${data['text_triggered']}
현재 감정: ${data['top_emotion']}
프롬프트: ${data['latest_prompt'] ?? '없음'}
감정 빈도: ${data['emotion_counter']}
'''),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: Text('닫기'),
              )
            ],
          ),
        );
      } else {
        _showError(context, '서버 응답 오류');
      }
    } catch (e) {
      _showError(context, '서버 상태 요청 실패');
    }
  }

  void _showError(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  void _applyUrl(BuildContext context) {
    setState(() {
      _baseUrl = _urlController.text.trim();
    });

    if (_baseUrl.isEmpty) {
      _showError(context, '서버 주소를 입력해주세요.');
      return;
    }

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('✅ 이제 $_baseUrl 으로 연결됩니다.')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: Text('STT 제어')),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: SingleChildScrollView(
              child: Builder(
                builder: (context) => Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    TextField(
                      controller: _urlController,
                      decoration: InputDecoration(
                        labelText: '서버 주소 입력 (예: http://192.168.0.2:8000)',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    SizedBox(height: 10),
                    ElevatedButton.icon(
                      icon: Icon(Icons.link),
                      label: Text('서버 주소 적용'),
                      onPressed: () => _applyUrl(context),
                    ),
                    SizedBox(height: 20),
                    Text(_text, style: TextStyle(fontSize: 20)),
                    SizedBox(height: 30),
                    ElevatedButton.icon(
                      icon: Icon(Icons.mic),
                      label: Text(_isListening ? '듣는 중...' : '음성 입력 시작'),
                      onPressed: _startListening,
                    ),
                    SizedBox(height: 10),
                    ElevatedButton.icon(
                      icon: Icon(Icons.send),
                      label: Text('텍스트 트리거 전송'),
                      onPressed: () => _stopListeningAndSendText(context),
                    ),
                    SizedBox(height: 10),
                    ElevatedButton.icon(
                      icon: Icon(Icons.face),
                      label: Text('감정 트리거 전송'),
                      onPressed: () => _sendEmotionTrigger(context),
                    ),
                    SizedBox(height: 10),
                    ElevatedButton.icon(
                      icon: Icon(Icons.refresh),
                      label: Text('리셋 트리거 전송'),
                      onPressed: () => _sendResetTrigger(context),
                    ),
                    SizedBox(height: 10),
                    ElevatedButton.icon(
                      icon: Icon(Icons.info_outline),
                      label: Text('서버 상태 보기'),
                      onPressed: () => _fetchServerStatus(context),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
