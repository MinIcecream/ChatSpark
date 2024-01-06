import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:permission_handler/permission_handler.dart';
import 'dart:io';
import 'package:audioplayers/audioplayers.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
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
  late StreamSubscription<RecordingDisposition> _recorderSubscription;

  @override
  void initState() {
    super.initState();
    player.onPlayerComplete.listen((_) {
      print("done playing");
    });
    initRecorder();

    print("done initializing");
  }

  @override
  void dispose() {
    recorder.closeRecorder();

    player.dispose();
    super.dispose();
  }

  Future initRecorder() async {
    final status = await Permission.microphone.request();

    if (status != PermissionStatus.granted) {
      throw "mic permission not granted!!";
    }
    await recorder.openRecorder();
  }

  Future record() async {
    print("starting recorder");
    await recorder.startRecorder(toFile: 'foo.mp4', codec: Codec.aacMP4);
    print("recorder started!");
  }

  Future stop() async {
    try {
      final path = await recorder.stopRecorder();
      final audioFile = File(path!);
      print("Saved audio at: $audioFile");
    } catch (e) {
      print("error stopping: $e");
    }
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
                  await player.play(DeviceFileSource('/data/user/0/com.example.chatspark/cache/foo.mp4'));
                },
                child: const Icon(Icons.play_arrow)),
          ],
        )));
  }
}
