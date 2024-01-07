import os
import time
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import chatbot
import asyncio 
from textToSpeech import speak
 
mostRecentResponse="Hey man!"
messages=[{"role":"system","content":"You are to return a conversation starter based on the messages you're given. Only return the conversation starter. Make it relevent to the conversation."}]

def print_current_response(messages):
    global mostRecentResponse
    mostRecentResponse=asyncio.run(chatbot.generate_response(messages))

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

#prolly returns transcription on end callback function. Need to implement
def transcribe_file():
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_API_KEY'), region="eastus")
    speech_config.speech_recognition_language="en-US"

    #use_default_microphone=True
    audio_config = speechsdk.audio.AudioConfig(filename="audio_files/katiesteve.wav")
    conversation_transcriber = speechsdk.transcription.ConversationTranscriber(speech_config=speech_config, audio_config=audio_config)

    transcribing_stop = False

    conversation_transcriber.transcribed.connect(file_transcribed_cb)  

    conversation_transcriber.start_transcribing_async()

    # Waits for completion.
    while not transcribing_stop:
        time.sleep(.5)
 
    conversation_transcriber.stop_transcribing_async()

def file_transcribed_cb(): 
    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print('TRANSCRIBED:')
        message = evt.result.text
        user = evt.result.speaker_id
        print('\tText={}'.format(message))
        print('\tSpeaker ID={}'.format(user)) 
# Main 
if __name__=="__main__":

    load_dotenv()
    transcribe_file()

