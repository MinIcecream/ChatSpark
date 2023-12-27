import os
import time
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import chatbot
 
 
def conversation_transcriber_recognition_canceled_cb(evt: speechsdk.SessionEventArgs):
    print('Canceled event')

def conversation_transcriber_session_stopped_cb(evt: speechsdk.SessionEventArgs):
    print('SessionStopped event')

def conversation_transcriber_transcribed_cb(evt: speechsdk.SpeechRecognitionEventArgs):
    print('TRANSCRIBED:')
    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print('\tText={}'.format(evt.result.text))
        print('\tSpeaker ID={}'.format(evt.result.speaker_id))
    # elif evt.result.reason == speechsdk.ResultReason.NoMatch:
    #     print('\tNOMATCH: Speech could not be TRANSCRIBED: {}'.format(evt.result.no_match_details))

        message=evt.result.text
        user=evt.result.speaker_id

        messages.append(message)

        #currentMessage=generateResponse(messages) 
        print(messages)

def conversation_transcriber_session_started_cb(evt: speechsdk.SessionEventArgs):
    print('SessionStarted event')

def recognize_from_mic():
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_API_KEY'), region="eastus")
    speech_config.speech_recognition_language="en-US"

    #use_default_microphone=True
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    conversation_transcriber = speechsdk.transcription.ConversationTranscriber(speech_config=speech_config, audio_config=audio_config)

    transcribing_stop = False

    def stop_cb(evt: speechsdk.SessionEventArgs):
        #"""callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        nonlocal transcribing_stop
        transcribing_stop = True

    # Connect callbacks to the events fired by the conversation transcriber
    conversation_transcriber.transcribed.connect(conversation_transcriber_transcribed_cb)
    conversation_transcriber.session_started.connect(conversation_transcriber_session_started_cb)
    conversation_transcriber.session_stopped.connect(conversation_transcriber_session_stopped_cb)
    conversation_transcriber.canceled.connect(conversation_transcriber_recognition_canceled_cb)
    # stop transcribing on either session stopped or canceled events
    conversation_transcriber.session_stopped.connect(stop_cb)
    conversation_transcriber.canceled.connect(stop_cb)

    conversation_transcriber.start_transcribing_async()

    # Waits for completion.
    while not transcribing_stop:
        time.sleep(.5)

    conversation_transcriber.stop_transcribing_async()

# Main 
if __name__=="__main__":

    currentMessage="Hey!"
    messages=["You are to return a conversation starter based on the messages you're given. Only return the conversation starter. Make it relevent to the conversation."]

    print("sup")

    load_dotenv()


    recognize_from_mic()

