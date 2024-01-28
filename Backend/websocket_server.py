import asyncio
import websockets 
from transcriber import Transcriber
import json
import os 
from dotenv import load_dotenv
import database_interface as db
import wave
 
usernames_map={} #maps username to websocket connection id

#Sends data to current client, if not none
async def send_data_to_client(client, data): 
    if(client is None):
       print("no client!")
       return  
    await client.send(data)

#Async function
#Checks every second if keyword was detected.
#If true, sends updated response to client
async def keyword_detected(transcriber_instance):
    while True:
        if transcriber_instance.keyword_detected:
            print("keyword detected...")
            transcriber_instance.keyword_detected=False 
            await send_data_to_client(usernames_map[transcriber_instance.client], transcriber_instance.get_response())
        await asyncio.sleep(1)

#Async function
#Receives raw audio data from client and adds it to the Queue
#Handles the channel closing and resets logs after client disconnects
async def add_to_buffer(websocket, path):    
    user_authenticated=False
    try:    
        while not user_authenticated:
            data = await websocket.recv()    
            data = json.loads(data) 
            if data["type"]=="authentication": 
                if db.authenticate_user(data["username"],data["password"]):
                    print("user logged in")
                    await websocket.send("success")
                    user_authenticated=True
                else:
                    if db.add_user_to_db(data["username"],data["password"]):
                        print("user registered!")
                        await websocket.send("success")
                        user_authenticated=True
                    else:
                        await websocket.send("false")
                        print("password incorrect!") 
    except websockets.exceptions.ConnectionClosedOK:
        print("connection closed!")
        return
    except websockets.exceptions.ConnectionClosedError:
        print("connection closed!")
        return
    finally:  
        pass

    client_username=data["username"]
    usernames_map[client_username]=websocket
    buffer = asyncio.Queue()  
    transcriber_instance=Transcriber.create_and_return_stream(client_username)
    write_to_stream=asyncio.create_task(write_queue_to_stream(transcriber_instance.stream, buffer)) 
    check_for_keyword=asyncio.create_task(keyword_detected(transcriber_instance))
    transcribe_from_stream=asyncio.create_task(transcriber_instance.recognize_from_stream())
    db.clear_user_messages_from_db(client_username)
    try:
        while True:
            data = await websocket.recv()    
            data = json.loads(data) 

            if data["type"]=="audio":  
                await buffer.put(bytes(data["payload"]))  
            elif data["type"]=="recordingStatus":
                if data["payload"]=="false":
                    db.clear_user_messages_from_db(client_username
                                                   )
    except websockets.exceptions.ConnectionClosedOK:
        print("connection closed!")
    except websockets.exceptions.ConnectionClosedError:
        print("connection closed!")
    finally:  
        db.clear_user_messages_from_db(client_username)
        usernames_map.pop(client_username,None)

#Async function
#Writes data from the Queue to the stream, which Azure API listens to.
async def write_queue_to_stream(stream, queue):
    try: 
        while True:
            audio_data = await queue.get()
            if audio_data is None:
                print("nothing received, exiting loops")
                break   
            try: 
                stream.write(audio_data) 
            except Exception as e:
                print("error: "+str(e))   

    except asyncio.CancelledError:
        pass

#Starts server.
async def start_server(): 
    ##initalize server and Queue for audio data 
    server = await websockets.serve(lambda ws, path: add_to_buffer(ws, path),os.environ.get("IP_ADDRESS"), 3000)
 
    print("WebSocket server started...") 
    #Start async functions  
    while(True):
        await asyncio.sleep(0.5)
     
 

# Run the main function
load_dotenv()
asyncio.run(start_server()) 
 