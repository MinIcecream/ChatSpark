import os 
import azure.cognitiveservices.speech as speechsdk 
import chatbot
import asyncio  
import json
import re
import database_interface as db

#Transcriber class that handles STT with Azure
class Transcriber:
    def __init__(self, client):
        self.client=client
        self.response="Hey man!"
        self.keyword="hello"
        self.keyword_detected=False
        self.stream=speechsdk.audio.PushAudioInputStream() 

    @classmethod
    def create_and_return_stream(cls, client):
        instance=cls(client)
        return instance 
 
    #Getter function used by server. Returns current response
    def get_response(self): 
        return self.response
    
    #Callback when a new message is trancribed
    async def transcribed_cb(self, evt):
        print(evt.result.speaker_id+": "+evt.result.text)
        
        #If keyword detected, raise flag. Otherwise, save to db
        if re.sub('[^a-zA-Z]', '', evt.result.text.lower()) ==self.keyword:
            self.keyword_detected=True
        else:
            asyncio.create_task(self.save_message_to_db(evt.result.speaker_id,evt.result.text))

    #Async function
    #Continuously reads from audio stream
    #Upon transcribing a message, calls save_message_to_logs()
    #Requires Api key to be set up in .env
    async def recognize_from_stream(self):   
        speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_API_KEY'), region="eastus")
        speech_config.speech_recognition_language="en-US"
        recognition_done=False
    
        audio_config=speechsdk.audio.AudioConfig(stream=self.stream)
        
        speech_recognizer=speechsdk.transcription.ConversationTranscriber(speech_config=speech_config, audio_config=audio_config)

        print("starting transcription for "+ str(self.client))
        def stopped_cb(evt):
            print("Session stopped!") 

        
        # Connect callbacks to the events fired by the conversation transcriber
        speech_recognizer.transcribed.connect(lambda evt:asyncio.run(self.transcribed_cb(evt)))
        speech_recognizer.session_started.connect(print("started transcribing!"))
        speech_recognizer.session_stopped.connect(stopped_cb) 
    
        speech_recognizer.start_transcribing_async()

        # Waits for completion.
        while not recognition_done: 
            await asyncio.sleep(.5)
        speech_recognizer.stop_transcribing_async() 

    #Saves a message to message logs. Used by transciber when a new message is transcribed.
    #Updates response
    async def save_message_to_db(self, speaker, content):
        db.add_message_to_db(self.client, speaker + ": "+content) 
        self.response=await chatbot.generate_response(self.client)  
    