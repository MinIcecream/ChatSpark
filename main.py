import os
import time
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
from chatbot import generate_response
import asyncio 

 
messages=[{"role":"system","content":"You are to return a conversation starter based on the messages you're given. Only return the conversation starter. Make it relevent to the conversation."}]
  
def print_current_response(messages):
    asyncio.run(generate_response(messages))

def conversation_transcriber_transcribed_cb(evt: speechsdk.SpeechRecognitionEventArgs):
    print('TRANSCRIBED:')
    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        message = evt.result.text
        user = evt.result.speaker_id
        print('\tText={}'.format(message))
        print('\tSpeaker ID={}'.format(user))

        new_message = {"role": "user", "content": message}
        messages.append(new_message)
        print_current_response(messages)
 
 
def recognize_from_mic():
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_API_KEY'), region="eastus")
    speech_config.speech_recognition_language="en-US"

    #use_default_microphone=True
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    conversation_transcriber = speechsdk.transcription.ConversationTranscriber(speech_config=speech_config, audio_config=audio_config)

    transcribing_stop = False

    # def stop_cb(evt: speechsdk.SessionEventArgs):
    #     #"""callback that signals to stop continuous recognition upon receiving an event `evt`"""
    #     print('CLOSING on {}'.format(evt))
    #     nonlocal transcribing_stop
    #     transcribing_stop = True

    # Connect callbacks to the events fired by the conversation transcriber
    conversation_transcriber.transcribed.connect(conversation_transcriber_transcribed_cb)  

    conversation_transcriber.start_transcribing_async()

    # Waits for completion.
    while not transcribing_stop:
        time.sleep(.5)
 
    conversation_transcriber.stop_transcribing_async()

# Main 
if __name__=="__main__":

    load_dotenv()
    recognize_from_mic()

