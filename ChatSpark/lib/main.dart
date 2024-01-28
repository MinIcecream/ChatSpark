import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:web_socket_channel/io.dart';

void main() {
  runApp(const MyApp());
}
class WebSocketManager {
  StreamController? controller;
  static final WebSocketManager instance = WebSocketManager._internal();
  IOWebSocketChannel? channel;

  factory WebSocketManager() {
    return instance;
  }

  WebSocketManager._internal() {
    // Initialize the controller here
    controller = StreamController.broadcast();
  }

  void connect() {
    // Check if the channel is already open and return if so
    if (channel != null) {
      print("WebSocket already connected.");
      return;
    }

    // Establish a new WebSocket connection
    channel = IOWebSocketChannel.connect(Uri.parse('ws://10.34.211.35:3000/'));

    // Listen to the new channel
    channel!.stream.listen((data) {
      // Check if controller is closed, and if so, do not add data to it
      if (!controller!.isClosed) {
        controller!.add(data);
      }
    }, onDone: () {
      // Close the controller when the WebSocket is done
      if (!controller!.isClosed) {
        controller!.close();
      }
    }, onError: (error) {
      if (!controller!.isClosed) {
        controller!.addError(error);
      }
    });

    print("Connected to WebSocket.");
  }

  Stream get stream {
    // Reinitialize the controller if it's closed
    if (controller == null || controller!.isClosed) {
      controller = StreamController.broadcast();
    }
    return controller!.stream;
  }

  void disconnect() {
    // Close the WebSocket connection
    if (channel != null) {
      channel!.sink.close();
      channel = null;
    }

    print("Disconnected from WebSocket.");
  }
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      home: LoginPage(),
    );
  }
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}


class _LoginPageState extends State<LoginPage> {
  final TextEditingController usernameController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  String? error;
  bool buttonDisabled=false;

  Future getAuthentication() async{
    var response= await WebSocketManager().stream.first;
    return response;
  }
  @override
  void initState() {
    WebSocketManager().connect();
    WebSocketManager().disconnect();
    WebSocketManager().connect();
    print("connecting to server.");
    super.initState();
  }
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.blue,
        title: const Text("Login/Sign Up"),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              enabled: buttonDisabled?false:true,
              controller: usernameController,
              decoration: const InputDecoration(
                labelText: "Username",
                icon: Icon(Icons.person),
              ),
            ),
            TextField(
              enabled: buttonDisabled?false:true,
              obscureText: true,
              controller: passwordController,
              decoration: const InputDecoration(
                labelText: "Password",
                icon: Icon(Icons.lock),
              ),
            ),
            if (error != null)
              Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8.0),
                  child: Text(
                    error!,
                    style: const TextStyle(color: Colors.red),
                  )),
            const SizedBox(height: 32.0),

            TextButton(
              onPressed:buttonDisabled? null:  () async {
                String password = passwordController.text;
                String username = usernameController.text;
                setState(() {
                  buttonDisabled=true;
                });

                if(username==""){
                  error="Username cannot be empty";
                  setState(() {});
                }
                else if(password==""){
                  error="Password cannot be empty";
                  setState(() {});
                }
                else{
                  setState(() {
                    error=null;
                  });
                  var response;
                  WebSocketManager().channel!.sink.add('{"type": "authentication", "username": "$username", "password":"$password"}');
                  print("last message...");
                  try{
                    response=await Future.any([
                      Future.delayed(const Duration(seconds:5)).then((_)=>null),
                      WebSocketManager().stream.first,
                    ]);
                  }
                  catch(e){
                    print("Error: $e");
                  }
                  print("done");
                  if (response==null){
                    setState(() {
                      buttonDisabled=false;
                      error="Error connecting to server";
                    });
                  }
                  else if (response == "success") {
                    print("YES");
                    setState(() {
                      error=null;
                    });
                    Navigator.push(context, MaterialPageRoute(builder: (context) => const MyHomePage()));
                  }
                  else
                  {
                    print("NO");
                    setState(() {
                      error = "Password incorrect";
                    });
                  }
                }
                setState(() {
                  buttonDisabled=false;
                });
              },
              child: const Text("Authenticate"),
            ),
          ],
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
  bool isRecorderReady = false;
  StreamSubscription? recordingSubscription;
  late FlutterTts flutterTts;

  var response = "How was your day?";

  @override
  void initState() {
    super.initState();

    flutterTts = FlutterTts();
    WebSocketManager().stream.listen((data) {
      print("response recieved!");
      response = data;
      setState(() {
      });
      speak();
    }, onDone: () {
      WebSocketManager().connect();
    }, onError: (error) {
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
    isRecorderReady = true;
  }

  @override
  void dispose() {
    recorder.closeRecorder();

    player.dispose();
    WebSocketManager().disconnect();
    WebSocketManager().connect();
    print("DONE CONNECTING");

    super.dispose();
  }

  Future record() async {
    assert(isRecorderReady);
    var recordingDataController = StreamController<Food>();
    recordingSubscription = recordingDataController.stream.listen((buffer) {
      if (buffer is FoodData) {
        var bufferData = buffer.data;
        WebSocketManager().channel!.sink.add('{"type": "audio", "payload": $bufferData}');
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
    WebSocketManager().channel!.sink.add('{"type": "recordingStatus", "payload": "false"}');
    if (recordingSubscription != null) {
      await recordingSubscription!.cancel();
      recordingSubscription = null;
    }
    setState(() {
      response="How was your day?";
    });
  }

  Future speak() async {
    print("SPEAKING!");
    recorder.pauseRecorder();
    await flutterTts.awaitSpeakCompletion(true);
    await flutterTts.speak(response);
    recorder.resumeRecorder();
    print("DONE SPEAKING!");
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
                width: 200,
                height: 100,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(10.0),
                  color: Colors.white70,
                ),
                child: Center(
                  child: Text(response),
                )),
            const SizedBox(height: 20),
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
        )));
  }
}
