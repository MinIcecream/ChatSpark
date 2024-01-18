// Flutter web plugin registrant file.
//
// Generated file. Do not edit.
//

// @dart = 2.13
// ignore_for_file: type=lint

import 'package:audioplayers_web/audioplayers_web.dart';
import 'package:flutter_sound_web/flutter_sound_web.dart';
import 'package:flutter_tts/flutter_tts_web.dart';
import 'package:permission_handler_html/permission_handler_html.dart';
import 'package:flutter_web_plugins/flutter_web_plugins.dart';

void registerPlugins([final Registrar? pluginRegistrar]) {
  final Registrar registrar = pluginRegistrar ?? webPluginRegistrar;
  AudioplayersPlugin.registerWith(registrar);
  FlutterSoundPlugin.registerWith(registrar);
  FlutterTtsPlugin.registerWith(registrar);
  WebPermissionHandler.registerWith(registrar);
  registrar.registerMessageHandler();
}
