import asyncio
from datetime import datetime
import json

async def handle_client(reader,writer):
    while True:
        data = await reader.read(1024)
        print(data.decode())


async def main():
    reader,writer = await asyncio.open_connection("127.0.0.1",9000)

    await asyncio.sleep(1)

    data = {
            "who":"rcs",
            "when":datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" ),
            "where":"cobot",
            "what":"write",
            "how":( 16, 9001, 1, (3,) ),
            "why":"request"
    }
    msg = json.dumps( data )
    writer.write(msg.encode())
    await writer.drain()

    await asyncio.sleep(1)
    

    data = {
            "who":"rcs",
            "when":datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" ),
            "where":"cobot",
            "what":"read",
            "how":( 3, 9001, 1 ),
            "why":"request"
    }
    msg = json.dumps( data )
    writer.write(msg.encode())
    await writer.drain()


asyncio.run(main())