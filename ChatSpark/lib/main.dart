import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:web_socket_channel/io.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

//ENTRY POINT OF FLUTTER APP
void main() async{
  await dotenv.load(fileName: ".env");
  runApp(const MyApp());
}

//SINGLETON THAT SAVES WEBSOCKET CHANNEL ACROSS PAGES
class WebSocketManager {
  StreamController? controller;
  static final WebSocketManager instance = WebSocketManager._internal();
  IOWebSocketChannel? channel;
  final address=dotenv.env['IP_ADDRESS'];

  factory WebSocketManager() {
    return instance;
  }

  WebSocketManager._internal() {
    // Initialize the controller here
    controller = StreamController.broadcast();
  }

  //Connects to channel and sets up stream controller
  void connect() {
    // Check if the channel is already open and return if so
    if (channel != null) {
      return;
    }

    // Establish a new WebSocket connection
    channel = IOWebSocketChannel.connect(Uri.parse('ws://${address!}:3000/'));
    controller = StreamController.broadcast();
    // Listen to the new channel
    channel!.stream.listen((data) {
      // Check if controller is closed, and if so, do not add data to it
      if (!controller!.isClosed) {
        controller!.add(data);
      }
    },);

  }

  Stream get stream {
    // Reinitialize the controller if it's closed
    if (controller == null || controller!.isClosed) {
      controller = StreamController.broadcast();
    }
    return controller!.stream;
  }

  //Disposes of channel and stream controller
  void disconnect() {
    // Close the WebSocket connection
    if (channel != null) {
      channel!.sink.close();
      channel = null;
    }
    if(controller!=null){
      controller!.close();
      controller=null;
    }
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

class _LoginPageState extends State<LoginPage> with WidgetsBindingObserver {
  final TextEditingController usernameController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  String? error;
  bool buttonDisabled=false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    WebSocketManager().connect();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    super.didChangeAppLifecycleState(state);
    if (state == AppLifecycleState.resumed) {
      // This block will execute when the LoginPage becomes visible again
      WebSocketManager().connect();
    }
  }
  //Authenticate button onClick.
  Future onClick() async {
    String password = passwordController.text;
    String username = usernameController.text;
    setState(() {
      buttonDisabled=true;
    });

    //Verifying fields aren't ampty
    if(username==""){
      error="Username cannot be empty";
      setState(() {});
    }
    else if(password==""){
      error="Password cannot be empty";
      setState(() {});
    }
    //Send data to server
    else{
      setState(() {
        error=null;
      });
      var response;

      WebSocketManager().connect();
      WebSocketManager().channel!.sink.add('{"type": "authentication", "username": "$username", "password":"$password"}');

      //Authenticating with server with timeout
      try{
        response=await Future.any([
          Future.delayed(const Duration(seconds:12)).then((_)=>null),
          WebSocketManager().stream.first,
        ]);
      }
      catch(e){
        throw("Error: $e");
      }
      //Server did not respond in time
      if (response==null){
        setState(() {
          buttonDisabled=false;
          error="Error connecting to server";
        });
      }
      //Successfully authenticated
      else if (response == "success") {
        setState(() {
          error=null;
        });
        Navigator.push(context, MaterialPageRoute(builder: (context) => const MyHomePage()));
      }
      //Password incorrect
      else
      {
        setState(() {
          error = "Password incorrect";
        });
      }
    }
    setState(() {
      buttonDisabled=false;
    });
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
              onPressed:buttonDisabled? null : ()=>onClick(),
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
  bool isRecorderReady = false;
  StreamSubscription? recordingSubscription;
  late FlutterTts flutterTts;

  var response = "How was your day?";

  @override
  void initState() {
    super.initState();

    flutterTts = FlutterTts();
    WebSocketManager().stream.listen((data) {
      response = data;
      setState(() {
      });
      speak();
    }, onDone: () {
    }, onError: (error) {
      throw "Error receiving data";
    });
    initRecorder();
  }

  //Gets mic permissions
  Future initRecorder() async {
    final status = await Permission.microphone.request();

    if (status != PermissionStatus.granted) {
      throw "mic permission not granted!!";
    }
    await recorder.openRecorder();
    isRecorderReady = true;
  }

  //Disposes of recorder and disconnects from server
  @override
  void dispose() {
    recorder.closeRecorder();
    WebSocketManager().disconnect();
    super.dispose();
  }

  //Records audio with mic
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

  //Stops recording
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

  //Uses STT to play current response
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
          title: const Text("Chatspark"),
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
