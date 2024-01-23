import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:web_socket_channel/io.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      home: LoginPage(),
    );
  }
}
class LoginPage extends StatelessWidget {
  const LoginPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.blue,
      ),
      body: Center(
        child: TextButton(
          child: const Text("Login"),
          onPressed: (){
            Navigator.push(context,MaterialPageRoute(builder:(context){
              return const MyHomePage();
            }));
          },
        ),
      ),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final recorder = FlutterSoundRecorder();
  final player = AudioPlayer();
  final IOWebSocketChannel channel = IOWebSocketChannel.connect('ws://10.34.211.35:3000/');
  bool isRecorderReady=false;
  StreamSubscription? recordingSubscription;
  late FlutterTts flutterTts;

  var response="How was your day?";


  @override
  void initState() {
    super.initState();

    flutterTts = FlutterTts();
    channel.stream.listen((data)
    {
      response=data;
      speak();
    }, onDone:(){
      print("Disconnecting from channel");
    }, onError:(error){
      throw "Error receiving data";
    });
    initRecorder();
  }

  Future initRecorder() async {
    final status = await Permission.microphone.request();

    if (status != PermissionStatus.granted) {
      throw "mic permission not granted!!";
    }
    await recorder.openRecorder();
    isRecorderReady=true;
  }

  @override
  void dispose() {
    recorder.closeRecorder();

    channel.sink.close();
    player.dispose();
    super.dispose();
  }

  Future record() async {
    assert(isRecorderReady);
    var recordingDataController = StreamController<Food>();
    recordingSubscription =
        recordingDataController.stream.listen((buffer) {
          if (buffer is FoodData) {
            var bufferData=buffer.data;
            channel.sink.add('{"type": "audio", "payload": $bufferData}');
          }
        });
    await recorder.startRecorder(
      toStream: recordingDataController.sink,
      codec: Codec.pcm16,
      numChannels: 1,
      sampleRate: 16000,
    );
    setState(() {});
  }

  Future stop() async {
    await recorder.stopRecorder();
    if (recordingSubscription != null) {
      await recordingSubscription!.cancel();
      recordingSubscription = null;
    }
  }

  Future speak() async {
    recorder.pauseRecorder();
    await flutterTts.awaitSpeakCompletion(true);
    await flutterTts.speak(response);
    recorder.resumeRecorder();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white70,
        appBar: AppBar(
          backgroundColor: Colors.orange,
          title: const Text("Audio Recorder"),
        ),
        body: Center(
            child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  width:200,
                  height:100,
                  padding:const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    borderRadius:BorderRadius.circular(10.0),
                    color:Colors.white70,
                  ),
                  child:Center(
                    child: Text(response),
                  )
                ),
              const SizedBox(height:20),
              ElevatedButton(
                child: Icon(recorder.isRecording ? Icons.stop : Icons.mic),
                onPressed: () async {
                  if (recorder.isRecording) {
                    await stop();
                  } else {
                    await record();
                  }
                  setState(() {});
                },
              ),
          ],
        )
      )
    );
  }
}
