import os
import time
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import chatbot
import asyncio 
from textToSpeech import speak
import json
 
mostRecentResponse="Hey man!"

def print_new_response():
    global mostRecentResponse
    try:
        with open("message_log.json", 'r') as file:
             messages = json.load(file)
    except:
        messages=[]
    mostRecentResponse=asyncio.run(chatbot.generate_response(messages))
""" 
def conversation_transcriber_transcribed_cb(evt: speechsdk.SpeechRecognitionEventArgs):
    if evt.result.text=="":
        print("Nothing transcribed")  

    elif evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print('TRANSCRIBED:')
        message = evt.result.text
        user = evt.result.speaker_id
        print('\tText={}'.format(message))
        print('\tSpeaker ID={}'.format(user))

        new_message = {"role": "user", "content": message}
        messages.append(new_message)

 
        print_current_response(messages) 
 
        if message.lower()=="hello.":
            print("keyword detected")
            speak(mostRecentResponse)
 
def recognize_from_mic():
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_API_KEY'), region="eastus")
    speech_config.speech_recognition_language="en-US"

    #use_default_microphone=True
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    conversation_transcriber = speechsdk.transcription.ConversationTranscriber(speech_config=speech_config, audio_config=audio_config)

    transcribing_stop = False

    conversation_transcriber.transcribed.connect(conversation_transcriber_transcribed_cb)  

    conversation_transcriber.start_transcribing_async()

    # Waits for completion.
    while not transcribing_stop:
        time.sleep(.5)
 
    conversation_transcriber.stop_transcribing_async()
 """

def transcribed_cb(evt: speechsdk.SpeechRecognitionEventArgs): 
    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech: 
        save_message_to_logs(evt.result.speaker_id,evt.result.text)


def transcribe_file():
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_API_KEY'), region="eastus")
    speech_config.speech_recognition_language="en-US"

    audio_config = speechsdk.audio.AudioConfig(filename="audio_files/test.wav")
    conversation_transcriber = speechsdk.transcription.ConversationTranscriber(speech_config=speech_config, audio_config=audio_config)

    transcribing_stop = False

    def stop_cb(evt: speechsdk.SessionEventArgs):
        #"""callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        nonlocal transcribing_stop
        transcribing_stop = True

    # Connect callbacks to the events fired by the conversation transcriber
    conversation_transcriber.transcribed.connect(transcribed_cb) 
    # stop transcribing on either session stopped or canceled events
    conversation_transcriber.session_stopped.connect(stop_cb)
    conversation_transcriber.canceled.connect(stop_cb)

    conversation_transcriber.start_transcribing_async()

    # Waits for completion.
    while not transcribing_stop:
        time.sleep(.5)

    conversation_transcriber.stop_transcribing_async()

def save_message_to_logs(speaker, content):
    try:
        with open("message_log.json", 'r') as file:
             messages = json.load(file)
    except:
        messages=[]
          
    new_message={"role": "user", "content": speaker+": "+content}
    messages.append(new_message)

    with open('message_log.json', 'w') as file:
        json.dump(messages, file, indent=2)

    print_new_response()

def clear_logs():
    try:
        with open("log_template.json", 'r') as file:
            messages = json.load(file)
    except:
        messages=[]
           
    with open('message_log.json', 'w') as file:
        json.dump(messages, file, indent=2)


# Main 
if __name__=="__main__":

    load_dotenv()
    clear_logs()

