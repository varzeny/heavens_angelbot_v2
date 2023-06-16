import asyncio
from module.server.server import Webserver

class Rcs:
    def __init__(self, name, addr) -> None:
        self.name = name
        self.addr = addr
        self.NETWORK = asyncio.Queue()
        self.UNITS = {}
        self.task = {}
        
        # module
        self.webserver = Webserver( self.NETWORK, self.UNITS, ("192.168.212.193",8000) )


    def run(self):
        print("Rcs 시작됨")
        try:
            self.loop = asyncio.get_event_loop()
            self.loop.create_task( self.main() )
            self.loop.run_forever()

        except Exception as e:
            print(self.name,"error run",e)

        print( "Rcs 종료됨" )


    async def main(self):
        # setup
        self.loop.create_task( self.checkQueue() )

        await self.NETWORK.put("aaa")



        # server start
        await self.webserver.run()
        print("종료됨")


    async def checkQueue(self):
        while True:
            try:
                msg = await self.NETWORK.get()
                self.loop.create_task( self.logic( msg ) )

            except Exception as e:
                print(self.name,"error checkQueue",e)
                continue


    async def logic(self, msg):
        try:
            print( msg )

            if msg == "aaa":
                await asyncio.sleep( 5 )
                await self.UNITS["unit_219"].handle_send("hahaha!!!")






        except Exception as e:
            print( self.name,f"logic 에서 msg : {msg} 처리중에 오류",e )








if __name__ == "__main__":
    rcs = Rcs( "heaven", ("127.0.0.1",8000) )
    rcs.run()
