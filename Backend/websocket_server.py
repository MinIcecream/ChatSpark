import asyncio
import websockets
import base64
import transcriber
import wave 
import chatbot
import json

client=None 

async def send_data_to_client(data): 
    if(client is None):
       return 
    await client.send(data)

async def keyword_detected():
    while True:
        if transcriber.keyword_detected:
            transcriber.keyword_detected=False
            print("sending to client!!")
            await send_data_to_client(transcriber.get_response())
        await asyncio.sleep(1)

#when data is recieved, add it to the queue. 
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
        pass
    except websockets.exceptions.ConnectionClosedError:
        print("connection closed!")
    finally: 
        transcriber.clear_logs()
        client=None


#Writes data from the queue to the .wav file and the stream
async def write_queue_to_wav(queue, output_file_path, sample_width=2, channels=1, sample_rate=16000):
    try:
        with wave.open(output_file_path, 'wb') as output_file:
            output_file.setnchannels(channels)
            output_file.setsampwidth(sample_width)
            output_file.setframerate(sample_rate) 
            
            while True:
                audio_data = await queue.get()
                if audio_data is None:
                    print("nothing recieved exiting loops")
                    break  # End the loop when None is received
                # Write the audio data to the WAV file 
                try:
                    transcriber.stream.write(audio_data)
                    #print("pushed to stream!")
                except Exception as e:
                    print("error: "+str(e)) 
                output_file.writeframes(audio_data)
                #print(f"Appended {len(audio_data)} bytes to {output_file_path}")

    except asyncio.CancelledError:
        pass

#Starts server.
async def start_server(): 
    ##initalize server and queue for audio data
    buffer = asyncio.Queue() 
    server = await websockets.serve(lambda ws, path: add_to_buffer(ws, path, buffer),'10.34.211.35', 3000)

    output_file_path="audio_files/output.wav"
    write_task = asyncio.create_task(write_queue_to_wav(buffer, output_file_path))
    asyncio.create_task(transcriber.recognize_from_stream())
    asyncio.create_task(keyword_detected())
    print("WebSocket server started...")

    await asyncio.sleep(9000)
    print("time limit hit...closing connection")

    server.close() 
    await server.wait_closed() 
 
    await buffer.put(None)  
 

# Run the main function
asyncio.run(start_server()) 
 