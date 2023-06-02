




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
        # await self.queue.put(b"test2")


        self.part["mobile"] = model_part.Part_Mobile(self.queue, "mobile", ("10.10.10.10",7171))
        self.part["cobot"] = model_part.Part_Cobot(self.queue, "cobot", ("192.168.1.2",502))

        # 큐체크
        print("큐 체크 시작")
        while True:
            msg = await self.queue.get()
            if msg == b"stop":
                break
            elif msg == b"init":
                self.loop.create_task(self.part["mobile"].connect())
                self.loop.create_task(self.part["cobot"].connect())
                await asyncio.sleep(2)
            elif msg == b"test1":
                await self.part["mobile"].sendMsg("say part mobile is ready")
                await asyncio.sleep(1)
                tcp = await self.part["cobot"].readRgs(7001,12)
                self.part["cobot"].tcp["x"]=tcp[0]
                self.part["cobot"].tcp["y"]=tcp[1]
                self.part["cobot"].tcp["z"]=tcp[2]
                self.part["cobot"].tcp["rx"]=tcp[3]
                self.part["cobot"].tcp["ry"]=tcp[4]
                self.part["cobot"].tcp["rz"]=tcp[5]
                print("cobot이 준비됨\n현재tcp :",self.part["cobot"].tcp)
            elif msg == b"test2":
                await self.part["cobot"].readRgs(7001,12)
                

        print("sbc의 main이 정지됨")

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
