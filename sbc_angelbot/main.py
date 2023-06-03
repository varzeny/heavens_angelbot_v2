




import asyncio
import websockets
import json

import module_part

##################################################################
class Sbc:
    def __init__(self,name) -> None:
        self.name = name
        self.queue = asyncio.Queue()
        self.loop = None
        self.module = {
            "sbc":None,
            "mobile":None,
            "cobot":None
        }

    def run(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete( self.main() )
        print("sbc의 run 이 종료함")
        
    ##################################################################

    async def main(self):


        self.module["mobile"] = module_part.Part_Mobile(self.queue, "mobile", ("10.10.10.10",7171))
        self.module["cobot"] = module_part.Part_Cobot(self.queue, "cobot", ("192.168.1.2",502))


        # 큐에 기본작업 넣어두기
        await self.queue.put(b"init")
        # await self.queue.put(b"test1")
        # await self.queue.put(b"test2")


        # 큐체크
        print("큐 체크 시작")
        while True:
            msg = await self.queue.get()
            if msg == b"stop":
                break
            elif msg == b"init":
                self.loop.create_task(self.module["mobile"].connect())
                self.loop.create_task(self.module["cobot"].connect())
                await asyncio.sleep(2)
            elif msg == b"test1":
                await self.module["mobile"].sendMsg("say part mobile is ready")
                await asyncio.sleep(1)
                tcp = await self.module["cobot"].readRgs(7001,12)
                self.module["cobot"].tcp["x"]=tcp[0]
                self.module["cobot"].tcp["y"]=tcp[1]
                self.module["cobot"].tcp["z"]=tcp[2]
                self.module["cobot"].tcp["rx"]=tcp[3]
                self.module["cobot"].tcp["ry"]=tcp[4]
                self.module["cobot"].tcp["rz"]=tcp[5]
                print("cobot이 준비됨\n현재tcp :",self.module["cobot"].tcp)
            elif msg == b"test2":
                await self.module["cobot"].readRgs(7001,12)
                

        print("sbc의 main이 정지됨")

    ##################################################################

    async def listen(self):
        self.server = await asyncio.start_server(
            self.handle_client,
            "127.0.0.1",
            7179
        )
        async with self.server:
            print(f"{self.name}의 서버가 기동함")
            await self.server.serve_forever()
        print(f"{self.name}의 서버가 정지함")

    async def handle_client(self, reader, writer):
        while True:
            recv = await reader.read(1024)
            if not recv:
                break
            elif recv[0] == '{':
                msg = json.loads(recv)
                self.queue.put(msg)
        
        print("클라이언트와 연결이 종료됨")

    ##################################################################
    







if __name__=="__main__":
    print("SBC 프로그램 시작됨")
    sbc = Sbc("unit_219")
    sbc.run()
