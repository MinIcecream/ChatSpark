import os
import time
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import chatbot
import asyncio  
import json
import wave
import test

mostRecentResponse="Hey man!" 

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
    wav_fh = wave.open("audio_files/output.wav")
    # Start pushing data until all data has been read from the file
    try: 
        while True:
            frames = wav_fh.readframes(n_bytes//2)
            print('read {} bytes'.format(len(frames)))
            if not frames:
                break
            test.stream.write(frames)
            await asyncio.sleep(.1)
    finally:
        wav_fh.close() 
        print("done pushign to stream")
  

def recognize_from_stream(): 
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_API_KEY'), region="eastus")
    speech_config.speech_recognition_language="en-US"
    recognition_done=False
 
    audio_config=speechsdk.audio.AudioConfig(stream=test.stream)
    
    speech_recognizer=speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    def stopped_cb(evt):
        print("Session stopped!")
        recognition_done=True

    speech_recognizer.session_started.connect(lambda evt:print("Session started!"))
    speech_recognizer.recognized.connect(lambda evt: print("Recognized: {}".format(evt)))
    speech_recognizer.session_stopped.connect(stopped_cb)
 
    speech_recognizer.start_continuous_recognition() 
    asyncio.run(push_stream_writer())
    while not recognition_done: 
        time.sleep(0.5)
    
    speech_recognizer.stop_continuous_recognition()

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
""" 
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
 """

# Main 
if __name__=="__main__":

    load_dotenv()
    recognize_from_stream()

