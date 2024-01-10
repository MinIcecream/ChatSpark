import asyncio
import websockets
import base64
import main
import wave
import test

cancel=False 

async def add_to_buffer(websocket, path, buffer):   
    try: 
        while True:
            data = await websocket.recv()    
            print(f"Received {len(data)} bytes")  
            await buffer.put(data) 
    except websockets.exceptions.ConnectionClosedOK:
        pass
    except websockets.exceptions.ConnectionClosedError:
        print("connection closed!")


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
                    test.stream.write(audio_data)
                    print("pushed to stream!")
                except Exception as e:
                    print("error: "+str(e)) 
                output_file.writeframes(audio_data)
                print(f"Appended {len(audio_data)} bytes to {output_file_path}")

    except asyncio.CancelledError:
        pass

async def start_server(): 
    buffer = asyncio.Queue() 
    server = await websockets.serve(lambda ws, path: add_to_buffer(ws, path, buffer),'192.168.0.173', 3000)

    output_file_path="audio_files/output.wav"
    write_task = asyncio.create_task(write_queue_to_wav(buffer, output_file_path))
    print("WebSocket server started...")

    await asyncio.sleep(30)
    print("time limit hit...closing connection")

    server.close() 
    await server.wait_closed() 
 
    await buffer.put(None)  
 

# Run the main function
asyncio.run(start_server()) 