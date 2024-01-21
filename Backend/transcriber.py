import os 
import azure.cognitiveservices.speech as speechsdk 
import chatbot
import asyncio  
import json
import re

#Default response
response="Hey man!"  

stream=speechsdk.audio.PushAudioInputStream()
keyword_detected=False

#phrase that triggers response
keyword="hello"

#Getter function used by server
def get_response(): 
    return response
 
#Async function
#Continuously reads from audio stream
#Upon transcribing a message, calls save_message_to_logs()
#Requires Api key to be set up in .env
async def recognize_from_stream():   
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_API_KEY'), region="eastus")
    speech_config.speech_recognition_language="en-US"
    recognition_done=False
 
    audio_config=speechsdk.audio.AudioConfig(stream=stream)
    
    speech_recognizer=speechsdk.transcription.ConversationTranscriber(speech_config=speech_config, audio_config=audio_config)

    def stopped_cb(evt):
        print("Session stopped!") 

    #Callback when a new message is trancribed
    async def transcribed_cb(evt):
        print(evt.result.speaker_id+": "+evt.result.text)
        global keyword
        if re.sub('[^a-zA-Z]', '', evt.result.text.lower()) ==keyword:
            global keyword_detected
            keyword_detected=True
        else:
            asyncio.create_task(save_message_to_logs(evt.result.speaker_id,evt.result.text))
 
    # Connect callbacks to the events fired by the conversation transcriber
    speech_recognizer.transcribed.connect(lambda evt:asyncio.run(transcribed_cb(evt)))
    speech_recognizer.session_started.connect(print("started transcribing!"))
    speech_recognizer.session_stopped.connect(stopped_cb) 
  
    speech_recognizer.start_transcribing_async()

    # Waits for completion.
    while not recognition_done:
        await asyncio.sleep(.5)
    speech_recognizer.stop_transcribing_async() 

#Clears message logs. Used by server when client disconnects
def clear_logs():
    try:
        with open("log_template.json", 'r') as file:
            messages = json.load(file)
    except:
        messages=[]
           
    with open('message_log.json', 'w') as file:
        json.dump(messages, file, indent=2)

#Saves a message to message logs. Used by transciber when a new message is transcribed.
async def save_message_to_logs(speaker, content):
    global response
    try:
        with open("message_log.json", 'r') as file:
             messages = json.load(file)
    except:
        messages=[]
        
    new_message={"role": "user", "content": speaker+": "+content}
    messages.append(new_message)

    with open('message_log.json', 'w') as file:
        json.dump(messages, file, indent=2)   
    response=await chatbot.generate_response(messages) 
 