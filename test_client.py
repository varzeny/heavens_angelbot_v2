import asyncio
from datetime import datetime
import json

async def handle_client(reader,writer):
    while True:
        data = await reader.read(1024)
        print(data.decode())


async def main():
    reader,writer = await asyncio.open_connection("127.0.0.1",7179)

    while True:
        inpu_data = input("입력하시오 : ")
        data = {
                "who":"rcs",
                "when":datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" ),
                "where":"cobot",
                "what":"write",
                "how":( 16, 8001, 1, (123,) ),
                "why":"request"
        }
        # data = {
        #         "who":"rcs",
        #         "when":datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" ),
        #         "where":"mobot",
        #         "what":"write",
        #         "how":"dotask move -100",
        #         "why":"request"
        # }
        # data = {
        #         "who":"rcs",
        #         "when":datetime.now().strftime( "%Y/%m/%d/%I/%M/%S/%f" ),
        #         "where":"mobot",
        #         "what":"write",
        #         "how":"dotask move 100",
        #         "why":"request"
        # }
        msg = json.dumps( data )
        writer.write(msg.encode())
        await writer.drain()


asyncio.run(main())