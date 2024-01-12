import os
import time
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import chatbot
import asyncio  
import json
import wave   

response="Hey man!" 
returning_response=False
time_since_last_transcription=0
stream=speechsdk.audio.PushAudioInputStream()

def print_new_response():
    global mostRecentResponse
    try:
        with open("message_log.json", 'r') as file:
             messages = json.load(file)
    except:
        messages=[]
    mostRecentResponse=asyncio.run(chatbot.generate_response(messages))

async def push_stream_writer():
    # The number of bytes to push per buffer
    n_bytes = 3200
    wav_fh = wave.open("audio_files/katiesteve.wav")
    # Start pushing data until all data has been read from the file
    try: 
        while True:
            frames = wav_fh.readframes(n_bytes//2)
            print('read {} bytes'.format(len(frames)))
            if not frames:
                break
            stream.write(frames)
            await asyncio.sleep(.1)
    finally:
        wav_fh.close() 
        print("done pushign to stream") 

async def increment_time_passed():
    global time_since_last_transcription
    while True:
        if not returning_response:
            await asyncio.sleep(0.5)
            time_since_last_transcription+=0.5

                 
        


async def recognize_from_stream():  
    global time_since_last_transcription

    asyncio.create_task(increment_time_passed())
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_API_KEY'), region="eastus")
    speech_config.speech_recognition_language="en-US"
    recognition_done=False
 
    audio_config=speechsdk.audio.AudioConfig(stream=stream)
    
    speech_recognizer=speechsdk.transcription.ConversationTranscriber(speech_config=speech_config, audio_config=audio_config)

    def stopped_cb(evt):
        print("Session stopped!")
        recognition_done=True

    def transcribed_cb(evt):
        print("recognized: {}".format(evt.result.text))
        save_message_to_logs(evt.result.speaker_id, evt.result.text)
        time_since_last_transcription=0

    # Connect callbacks to the events fired by the conversation transcriber
    speech_recognizer.transcribed.connect(transcribed_cb)
    speech_recognizer.session_started.connect(lambda evt:print("Session started!"))
    speech_recognizer.session_stopped.connect(stopped_cb) 
  
    speech_recognizer.start_transcribing_async()

    # Waits for completion.
    while not recognition_done:
        await asyncio.sleep(.5)

    speech_recognizer.stop_transcribing_async()

""" async def push_to_stream(stream): 
    num_bytes=3200

    file=wave.open("katiesteve.wav")

    try:
        while True:
            frames=file.readframes(num_bytes // 2)
            print("read {} bytes".format(len(frames)))
            if not frames:
                break
            stream.write(frames)
            asyncio.sleep(.1)
    finally:
        file.close()
        stream.close() """

def save_message_to_logs(speaker, content):
    try:
        with open("message_log.json", 'r') as file:
             messages = json.load(file)
    except:
        messages=[]
    print("new message and content: "+speaker+content)
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


async def start_program(): 
    task1 = asyncio.create_task(recognize_from_stream())
    task2 = asyncio.create_task(push_stream_writer())
    
    await asyncio.gather(task1, task2)

# Main 
if __name__=="__main__":

    load_dotenv()
    asyncio.run(start_program()) 

