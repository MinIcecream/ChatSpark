import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:permission_handler/permission_handler.dart';
import 'dart:io';
import 'package:audioplayers/audioplayers.dart';
import 'package:web_socket_channel/io.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      home: MyHomePage(),
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
    flutterTts = FlutterTts();

    super.initState();
    channel.stream.listen((data)
    {
      response=data;
      speak();
      print("Received: $data");
    }, onDone:(){
      print("Websocket closed");
    }, onError:(error){
      print("Error: $error");
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
        appBar: AppBar(
          backgroundColor: Colors.blue,
          title: const Text("Audio Recorder"),
        ),
        body: Center(
            child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(response),
              ElevatedButton(
                child: Icon(recorder.isRecording ? Icons.stop : Icons.mic),
                onPressed: () async {
                  if (recorder.isRecording) {
                    print("going to stop now");
                    await stop();
                  } else {
                    print("going to record now");
                    await record();
                  }
                  setState(() {});
                },
              ),
              ElevatedButton(
                  onPressed: () async {
                    print("playing");
                    await speak();
                  },
                  child: const Icon(Icons.play_arrow)
              ),
          ],
        )
      )
    );
  }
}
