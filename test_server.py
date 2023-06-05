import asyncio




async def handle_client(reader,writer):
    while True:
        msg = await reader.read(1024)
        print(msg)

async def listen():
    server = await asyncio.start_server(
        handle_client,
        "10.10.10.51",
        7179
    )
    await server.serve_forever()

asyncio.run( listen() )