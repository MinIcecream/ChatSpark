import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_sound/flutter_sound.dart';
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
  final IOWebSocketChannel channel = IOWebSocketChannel.connect('ws://192.168.0.173:3000/');
  bool isRecorderReady=false;
  StreamSubscription? recordingSubscription;


  @override
  void initState() {
    super.initState();
    player.onPlayerComplete.listen((_) {
      print("done playing");
    });
    channel.stream.listen((data)
    {
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
            print("sending");
            channel.sink.add(buffer.data!);
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


  Future<void> sendMp4File() async {
    try {
      String filePath = "/data/user/0/com.example.chatspark/cache/foo.wav";
      File wavFile = File(filePath);
      Uint8List wavBytes = await wavFile.readAsBytes();
      channel.sink.add(wavBytes);
    } catch (e) {
      print('Error: $e');
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
                    await player.play(DeviceFileSource('/data/user/0/com.example.chatspark/cache/foo.wav'));
                  },
                  child: const Icon(Icons.play_arrow)
              ),
              ElevatedButton(
                onPressed: () async{
                  await sendMp4File();
                },
                child: const Icon(Icons.send)
            ),
          ],
        )
      )
    );
  }
}
