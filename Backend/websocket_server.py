import asyncio
import websockets 
from transcriber import Transcriber
import json
import os 
from dotenv import load_dotenv
import database_interface as db
import wave
 
usernames_map={} #maps username to websocket connection id
 
#Async function
#Sends data to client, if not none
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
            transcriber_instance.keyword_detected=False 
            await send_data_to_client(usernames_map[transcriber_instance.client], transcriber_instance.get_response())
        await asyncio.sleep(1)

#Async function
#Receives raw audio data from client and adds it to the Queue
#Handles the channel closing and resets logs after client disconnects
async def add_to_buffer(websocket, path):    

    #Handles user authentication.
    user_authenticated=False
    try:    
        while not user_authenticated:
            data = await websocket.recv()    
            data = json.loads(data) 

            if data["type"]=="authentication": 
                #If username and password are correct, login
                if db.authenticate_user(data["username"],data["password"]):
                    print("user logged in")
                    await websocket.send("success")
                    user_authenticated=True
                else:
                    #If username is new, register new user
                    if db.add_user_to_db(data["username"],data["password"]):
                        print("user registered!")
                        await websocket.send("success")
                        user_authenticated=True
                    else:
                        #Password is wrong
                        await websocket.send("false")
                        print("password incorrect!") 

    except websockets.exceptions.ConnectionClosedOK:
        print("connection closed!")
        return
    except websockets.exceptions.ConnectionClosedError:
        print("connection closed!")
        return 

    #Once client is authenticated, start async functions.

    #Initializing variables
    client_username=data["username"]
    usernames_map[client_username]=websocket
    buffer = asyncio.Queue()  
    transcriber_instance=Transcriber.create_and_return_stream(client_username)

    db.clear_user_messages_from_db(client_username)

    #Starting async functions
    write_to_stream=asyncio.create_task(write_queue_to_stream(transcriber_instance.stream, buffer)) 
    check_for_keyword=asyncio.create_task(keyword_detected(transcriber_instance))
    transcribe_from_stream=asyncio.create_task(transcriber_instance.recognize_from_stream()) 

    #Start receiving audio data
    try:
        while True:
            #Receive data from websocket connection and add it to a queue
            data = await websocket.recv()    
            data = json.loads(data) 

            if data["type"]=="audio":  
                await buffer.put(bytes(data["payload"]))  
            elif data["type"]=="recordingStatus":
                if data["payload"]=="false":
                    db.clear_user_messages_from_db(client_username)
    finally:  
        #When client disconnects, remove them from the map and clear their messages
        db.clear_user_messages_from_db(client_username)
        usernames_map.pop(client_username,None)

        #Cancel async functions
        write_to_stream.cancel()
        check_for_keyword.cancel()
        transcribe_from_stream.cancel()

#Async function
#Takes in a stream and a queue. Writes contents of queue to the stream
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

#Starts server
#Requires local IP to be set up in .env
async def start_server(): 
    ##initalize server
    server = await websockets.serve(lambda ws, path: add_to_buffer(ws, path),os.environ.get("IP_ADDRESS"), 3000) 
    print("WebSocket server started...") 

    #Runs indefinitely
    while(True):
        await asyncio.sleep(0.5)
     
 

# Run the main function
load_dotenv()
asyncio.run(start_server()) 
 