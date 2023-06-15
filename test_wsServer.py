import asyncio
import websockets

CONNECTED = {}

async def handle_connection(websocket, path):
    print( websocket.remote_address,"가 접속함" )
    CONNECTED[websocket.remote_address] = websocket

    try:
        async for message in websocket:
            print(path, message)

        print("Client connection closed")
        del CONNECTED[websocket.remote_address]


    except Exception as e:
        print("클라이언트 종료됨")

async def start_server():
    server = await websockets.serve(handle_connection, 'localhost', 8000)
    print("WebSocket server started")

    await server.wait_closed()

asyncio.run(start_server())
