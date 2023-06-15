import asyncio
import websockets


class Client:
    def __init__(self):
        self.CONNECTED = {}
        self.task = {}
        self.loop = None

    def run(self):
        self.loop = asyncio.get_event_loop()
        self.loop.create_task( self.main() )
        self.loop.run_forever()


    async def main(self):
        self.task["connect"] = self.loop.create_task( self.connect() )


        await asyncio.sleep( 2 )
        
        while True:
            self.task["send"] = self.loop.create_task( self.handle_send("hi") )
            await asyncio.sleep(1)


    async def connect(self):
        while True:
            try:
                websocket = await websockets.connect('ws://localhost:8000/abc')
                print("접속 성공")
                self.CONNECTED["kim"] = websocket

            except Exception as e:
                print("접속 실패, 재접속 시도 중.......")
                await asyncio.sleep(1)
                continue

            try:
                async for msg in websocket:
                    print( msg )

            except Exception as e:
                print("수신 대기 중 오류")

            finally:
                await asyncio.sleep(2)



    async def handle_send( self, msg ):
        try:
            await self.CONNECTED["kim"].send( msg )
            
        except Exception as e:
            print( "error handle_send")


if __name__=="__main__":
    c = Client()
    c.run()



