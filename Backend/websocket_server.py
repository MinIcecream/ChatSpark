import asyncio
import websockets 
import transcriber  
import json
import os 
from dotenv import load_dotenv

#Keeps track of current websocket client
client=None 

#Sends data to current client, if not none
async def send_data_to_client(data): 
    if(client is None):
       return 
    await client.send(data)

#Async function
#Checks every second if keyword was detected.
#If true, sends updated response to client
async def keyword_detected():
    while True:
        if transcriber.keyword_detected:
            transcriber.keyword_detected=False 
            await send_data_to_client(transcriber.get_response())
        await asyncio.sleep(1)

#Async function
#Receives raw audio data from client and adds it to the Queue
#Handles the channel closing and resets logs after client disconnects
async def add_to_buffer(websocket, path, buffer):    
    global client
    try:  
        client = websocket
        while True: 
            data = await websocket.recv()    

            data = json.loads(data) 
            if data["type"]=="audio": 
                await buffer.put(bytes(data["payload"]))  

    except websockets.exceptions.ConnectionClosedOK:
        print("connection closed!")
    except websockets.exceptions.ConnectionClosedError:
        print("connection closed!")
    finally: 
        transcriber.clear_logs()
        client=None

#Async function
#Writes data from the Queue to the stream, which Azure API listens to.
async def write_queue_to_stream(queue):
    try:
        while True:
            audio_data = await queue.get()
            if audio_data is None:
                print("nothing received, exiting loops")
                break   
            try:
                transcriber.stream.write(audio_data) 
            except Exception as e:
                print("error: "+str(e))  

    except asyncio.CancelledError:
        pass

#Starts server.
async def start_server(): 
    ##initalize server and Queue for audio data
    buffer = asyncio.Queue() 
    server = await websockets.serve(lambda ws, path: add_to_buffer(ws, path, buffer),os.environ.get("IP_ADDRESS"), 3000)
 
    #Start async functions
    write_to_stream=asyncio.create_task(write_queue_to_stream(buffer))
    speech_transcriber=asyncio.create_task(transcriber.recognize_from_stream())
    check_for_keyword=asyncio.create_task(keyword_detected())
    
    await asyncio.gather(write_to_stream,speech_transcriber,check_for_keyword)
    print("WebSocket server started...")
 

# Run the main function
load_dotenv()
asyncio.run(start_server()) 
 