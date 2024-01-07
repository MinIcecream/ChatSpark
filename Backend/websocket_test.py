import asyncio
import websockets
import base64



async def handle_websocket(websocket, path):
    try: 
       data = await websocket.recv() 
       with open("audio_files/test.wav", 'wb') as wav_file:
            wav_file.write(data)
    except websockets.exceptions.ConnectionClosedOK:
        pass
  

async def main():
    server = await websockets.serve(handle_websocket, '192.168.0.173', 3000)
    print("WebSocket server started...")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())