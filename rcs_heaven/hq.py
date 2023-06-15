import asyncio


from rcs_heaven.module.server.server import server as srv


class Rcs:
    def __init__(self, name, addr) -> None:
        self.name = name
        self.addr = addr
        self.Q_rcs = asyncio.Queue()
        self.units = {}

    def run(self):
        try:
            print("--------rcs 시작됨")
            self.loop = asyncio.get_event_loop()

            # startup task
            self.loop.create_task( self.checkQueue() )
            self.loop.create_task( self.runServer() )

            self.loop.run_forever()

        except Exception as e:
            print("--------rcs 기동이 중지됨",e)

    #########################################################################

    async def runServer(self):
        try:
            server = await srv
            

        except Exception as e:
            print(self.name,"error runServer",e)
            
    #########################################################################


    async def checkQueue(self):
        while True:
            try:
                msg = await self.Q_rcs.get()
                self.loop.create_task( self.logic( msg ) )
            
            except Exception as e:
                print(self.name, "----error checkQueue",e)
                continue

    #########################################################################

    async def logic(self, msg):

        where = msg["where"]
        who = msg["who"]
        when = msg["when"]
        what = msg["what"]
        how = msg["how"]
        why = msg["why"]

        try:
            if msg["where"] == "status":
                pass

            
        except Exception as e:
            pass








if __name__=="__main__":
    heaven = Rcs("heaven")
