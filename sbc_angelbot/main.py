




import asyncio
import websockets

import model_logic
import model_part

##################################################################
class Sbc:
    def __init__(self,name) -> None:
        self.name = name
        self.queue = asyncio.Queue()
        self.part = {
            "mobile":None,
            "cobot":None
        }
        self.server = None
        self.loop = None

    def run(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete( self.main() )
        print("sbc의 run 이 종료함")
        
    ##################################################################

    async def main(self):

        await self.queue.put(b"init")
        await self.queue.put(b"test1")


        self.part["mobile"] = model_part.Part_Mobile(self.queue, "mobile", ("10.10.10.10",7171))
        self.part["cobot"] = model_part.Part_Cobot(self.queue, "cobot", ("192.168.215.101",502))

        while True:
            msg = await self.queue.get()
            if msg == b"stop":
                break
            elif msg == b"init":
                self.loop.create_task(self.part["mobile"].connect())
                self.loop.create_task(self.part["cobot"].connect())
            elif msg == b"test1":
                print("haha")
                await asyncio.sleep(2)
                await self.part["mobile"].sendMsg("say hahaha")
                
            print(msg)
            print()

        print("sbc의 main이 정지됨")

    ##################################################################
    async def connect(self,addr):
        reader, writer = asyncio.open_connection(addr[0],addr[1])

    ##################################################################

    async def listen(self):
        self.server = await asyncio.start_server(
            self.handle_client,
            "127.0.0.1",
            7179
        )
        async with self.server:
            await self.server.serve_forever()
        
        print("서버가 정지함")

    async def handle_client(self, reader, writer):

        while True:
            msg = await reader.read(1024)
            if not msg:
                break
            self.queue.put(msg)
        
        print("클라이언트와 연결이 종료됨")

    ##################################################################
    







if __name__=="__main__":
    print("프로그램 시작됨")
    sbc = Sbc("unit_219")
    sbc.run()
